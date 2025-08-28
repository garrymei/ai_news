#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能新闻图片生成器
根据新闻内容语义分析，生成贴合主题的专业图片
支持多种MCP图片生成服务
"""
import os, json, glob, datetime, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random, requests, re
from dateutil.tz import tzlocal
import base64
from io import BytesIO

# 配置
W, H = 1080, 1920
FONT_PATH = "/System/Library/Fonts/Hiragino Sans GB.ttc"

def latest(path):
    files = sorted(glob.glob(path), reverse=True)
    return files[0] if files else ""

def analyze_news_content(title, summary):
    """分析新闻内容，提取关键信息用于图片生成"""
    content = (title + " " + summary).lower()
    
    analysis = {
        "主题": "technology",
        "公司": [],
        "产品": [],
        "技术": [],
        "颜色方案": "blue",
        "风格": "corporate",
        "图标元素": []
    }
    
    # 公司识别
    companies = {
        "openai": {"name": "OpenAI", "color": "green", "icon": "brain"},
        "anthropic": {"name": "Anthropic", "color": "orange", "icon": "chat"},
        "microsoft": {"name": "Microsoft", "color": "blue", "icon": "windows"},
        "google": {"name": "Google", "color": "multicolor", "icon": "search"},
        "apple": {"name": "Apple", "color": "gray", "icon": "apple"},
        "meta": {"name": "Meta", "color": "blue", "icon": "vr"},
        "nvidia": {"name": "NVIDIA", "color": "green", "icon": "chip"},
        "tesla": {"name": "Tesla", "color": "red", "icon": "car"},
        "mit": {"name": "MIT", "color": "red", "icon": "university"}
    }
    
    for key, info in companies.items():
        if key in content:
            analysis["公司"].append(info)
            analysis["颜色方案"] = info["color"]
            analysis["图标元素"].append(info["icon"])
    
    # 产品/技术识别
    products = {
        "gpt": {"name": "GPT", "type": "AI模型", "visual": "neural_network"},
        "claude": {"name": "Claude", "type": "AI助手", "visual": "assistant_bot"},
        "chatgpt": {"name": "ChatGPT", "type": "对话AI", "visual": "chat_interface"},
        "dalle": {"name": "DALL-E", "type": "图像生成", "visual": "image_creation"},
        "机器人": {"name": "Robot", "type": "机器人", "visual": "robot_arm"},
        "自动驾驶": {"name": "Autonomous", "type": "自动驾驶", "visual": "car_sensors"},
        "芯片": {"name": "Chip", "type": "芯片", "visual": "circuit_board"},
        "算法": {"name": "Algorithm", "type": "算法", "visual": "flowchart"}
    }
    
    for key, info in products.items():
        if key in content:
            analysis["产品"].append(info)
            analysis["图标元素"].append(info["visual"])
    
    # 主题分析
    if any(word in content for word in ["发布", "推出", "宣布"]):
        analysis["主题"] = "product_launch"
        analysis["风格"] = "announcement"
    elif any(word in content for word in ["突破", "创新", "研发"]):
        analysis["主题"] = "innovation"
        analysis["风格"] = "research"
    elif any(word in content for word in ["合作", "收购", "投资"]):
        analysis["主题"] = "business"
        analysis["风格"] = "corporate"
    elif any(word in content for word in ["安全", "隐私", "监管"]):
        analysis["主题"] = "security"
        analysis["风格"] = "serious"
    
    return analysis

def get_theme_colors(analysis):
    """根据分析结果获取颜色方案"""
    color_schemes = {
        "green": [(34, 197, 94), (74, 222, 128)],      # OpenAI绿
        "orange": [(249, 115, 22), (251, 146, 60)],    # Anthropic橙
        "blue": [(59, 130, 246), (147, 197, 253)],     # 科技蓝
        "red": [(239, 68, 68), (248, 113, 113)],       # MIT红
        "purple": [(147, 51, 234), (167, 139, 250)],   # 创新紫
        "gray": [(107, 114, 128), (156, 163, 175)],    # Apple灰
        "multicolor": [(59, 130, 246), (34, 197, 94)]  # Google多彩
    }
    
    return color_schemes.get(analysis["颜色方案"], color_schemes["blue"])

def create_semantic_background(analysis, width=W, height=H):
    """根据语义分析创建背景"""
    colors = get_theme_colors(analysis)
    
    # 创建基础渐变
    img = Image.new('RGB', (width, height), colors[0])
    
    # 根据主题选择渐变样式
    if analysis["主题"] == "product_launch":
        # 产品发布：中心放射渐变
        for y in range(height):
            for x in range(width):
                center_x, center_y = width//2, height//3
                distance = ((x - center_x)**2 + (y - center_y)**2)**0.5
                max_distance = width * 0.8
                ratio = min(distance / max_distance, 1.0)
                
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                
                img.putpixel((x, y), (r, g, b))
    
    elif analysis["主题"] == "innovation":
        # 创新研究：对角渐变
        for y in range(height):
            ratio = y / height * 0.8 + (height - y) / height * 0.2
            for x in range(width):
                x_ratio = x / width * 0.3
                final_ratio = (ratio + x_ratio) / 1.3
                
                r = int(colors[0][0] * (1 - final_ratio) + colors[1][0] * final_ratio)
                g = int(colors[0][1] * (1 - final_ratio) + colors[1][1] * final_ratio)
                b = int(colors[0][2] * (1 - final_ratio) + colors[1][2] * final_ratio)
                
                img.putpixel((x, y), (r, g, b))
    
    else:
        # 默认：垂直渐变
        for y in range(height):
            ratio = y / height
            color = tuple(int(colors[0][i] * (1 - ratio) + colors[1][i] * ratio) for i in range(3))
            for x in range(width):
                img.putpixel((x, y), color)
    
    return img

def add_semantic_elements(img, analysis):
    """根据语义分析添加相关视觉元素"""
    draw = ImageDraw.Draw(img)
    
    # 为不同主题添加特定图案
    if "neural_network" in analysis["图标元素"]:
        # 添加神经网络图案
        add_neural_network_pattern(img)
    
    if "robot_arm" in analysis["图标元素"]:
        # 添加机器人相关图案
        add_robotics_pattern(img)
    
    if "circuit_board" in analysis["图标元素"]:
        # 添加电路板图案
        add_circuit_pattern(img)
    
    # 添加公司特色元素
    for company in analysis["公司"]:
        if company["name"] == "OpenAI":
            add_openai_elements(img)
        elif company["name"] == "Anthropic":
            add_anthropic_elements(img)
        elif company["name"] == "MIT":
            add_academic_elements(img)
    
    return img

def add_neural_network_pattern(img):
    """添加神经网络图案"""
    overlay = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 绘制节点和连接线
    nodes = []
    for layer in range(3):
        for node in range(4):
            x = 150 + layer * 200
            y = 200 + node * 100
            nodes.append((x, y))
            # 绘制节点
            draw.ellipse([x-15, y-15, x+15, y+15], fill=(255, 255, 255, 60))
    
    # 绘制连接线
    for i in range(len(nodes)-1):
        for j in range(i+1, len(nodes)):
            if abs(nodes[i][0] - nodes[j][0]) < 250:  # 只连接相邻层
                draw.line([nodes[i], nodes[j]], fill=(255, 255, 255, 30), width=2)
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img

def add_robotics_pattern(img):
    """添加机器人图案"""
    overlay = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 绘制机械臂风格的几何图形
    for i in range(3):
        x = 200 + i * 150
        y = 150 + i * 80
        # 关节
        draw.ellipse([x-20, y-20, x+20, y+20], fill=(255, 255, 255, 40))
        # 连接杆
        if i < 2:
            next_x = 200 + (i+1) * 150
            next_y = 150 + (i+1) * 80
            draw.line([(x, y), (next_x, next_y)], fill=(255, 255, 255, 50), width=8)
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img

def add_circuit_pattern(img):
    """添加电路板图案"""
    overlay = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 绘制电路线条
    for i in range(0, W, 80):
        draw.line([(i, 0), (i, H//3)], fill=(255, 255, 255, 25), width=2)
        for j in range(0, H//3, 60):
            draw.line([(0, j), (W, j)], fill=(255, 255, 255, 25), width=1)
            # 添加电路节点
            if i % 160 == 0 and j % 120 == 0:
                draw.rectangle([i-5, j-5, i+5, j+5], fill=(255, 255, 255, 60))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img

def add_openai_elements(img):
    """添加OpenAI风格元素"""
    overlay = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # OpenAI的螺旋图案
    center_x, center_y = W//4, H//4
    for angle in range(0, 360, 5):
        import math
        radius = 30 + angle * 0.2
        x = center_x + radius * math.cos(math.radians(angle))
        y = center_y + radius * math.sin(math.radians(angle))
        draw.ellipse([x-3, y-3, x+3, y+3], fill=(255, 255, 255, 40))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img

def add_anthropic_elements(img):
    """添加Anthropic风格元素"""
    overlay = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 对话气泡风格的图案
    for i in range(3):
        x = W//2 + i * 80
        y = 200 + i * 100
        # 气泡
        draw.ellipse([x-40, y-30, x+40, y+30], outline=(255, 255, 255, 60), width=3)
        # 小圆点
        for j in range(3):
            dot_x = x - 15 + j * 15
            draw.ellipse([dot_x-3, y-3, dot_x+3, y+3], fill=(255, 255, 255, 80))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img

def add_academic_elements(img):
    """添加学术研究风格元素"""
    overlay = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 网格和图表风格
    for i in range(5):
        y = 100 + i * 80
        # 横线
        draw.line([(50, y), (W-50, y)], fill=(255, 255, 255, 30), width=2)
        # 数据点
        for j in range(8):
            x = 100 + j * 120
            height = random.randint(10, 60)
            draw.rectangle([x-10, y-height, x+10, y], fill=(255, 255, 255, 50))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img

def create_smart_news_image(title, summary, source, output_path):
    """创建智能新闻图片"""
    print(f"  🧠 分析新闻语义: {title[:30]}...")
    
    # 语义分析
    analysis = analyze_news_content(title, summary)
    print(f"  📊 主题: {analysis['主题']}, 公司: {[c['name'] for c in analysis['公司']]}")
    print(f"  🎨 颜色方案: {analysis['颜色方案']}, 图标: {analysis['图标元素']}")
    
    # 创建语义背景
    img = create_semantic_background(analysis)
    
    # 添加语义元素
    img = add_semantic_elements(img, analysis)
    
    # 添加文字层
    img = img.convert('RGBA')
    
    # 文字背景
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 顶部品牌区域
    draw.rectangle([(0, 0), (W, 200)], fill=(0, 0, 0, 120))
    
    # 底部文字区域  
    draw.rectangle([(0, H*2//3), (W, H)], fill=(0, 0, 0, 150))
    
    img = Image.alpha_composite(img, overlay)
    
    # 添加文字
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        font_large = ImageFont.truetype(FONT_PATH, 68)
        font_medium = ImageFont.truetype(FONT_PATH, 44)
        font_small = ImageFont.truetype(FONT_PATH, 34)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # 品牌和来源
    draw.text((60, 60), "AI科技速递", font=font_medium, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0,0,0))
    
    # 公司标识
    if analysis["公司"]:
        company_text = " | ".join([c["name"] for c in analysis["公司"][:2]])
        draw.text((60, 120), f"🏢 {company_text}", font=font_small, fill=(200, 200, 200))
    
    draw.text((60, 160), f"📰 {source}", font=font_small, fill=(180, 180, 180))
    
    # 主标题智能换行
    y_pos = H*2//3 + 60
    title_lines = []
    
    if len(title) > 18:
        # 寻找最佳断点
        break_chars = "，。！？、发布宣布推出"
        best_break = len(title) // 2
        
        for i in range(len(title)//2 - 6, len(title)//2 + 6):
            if i < len(title) and title[i] in break_chars:
                best_break = i + 1
                break
        
        title_lines = [title[:best_break].strip(), title[best_break:].strip()]
    else:
        title_lines = [title]
    
    # 绘制标题
    for i, line in enumerate(title_lines):
        if line:
            draw.text((60, y_pos + i * 90), line, font=font_large, fill=(255, 255, 255), 
                     stroke_width=2, stroke_fill=(0,0,0))
    
    # 摘要
    y_pos += len(title_lines) * 90 + 40
    summary_lines = []
    if len(summary) > 40:
        mid = len(summary) // 2
        for i in range(mid-10, mid+10):
            if i < len(summary) and summary[i] in "。！？，":
                summary_lines = [summary[:i+1], summary[i+1:]]
                break
        else:
            summary_lines = [summary[:40] + "...", summary[40:80] + "..."]
    else:
        summary_lines = [summary]
    
    for i, line in enumerate(summary_lines[:2]):
        if line.strip():
            draw.text((60, y_pos + i * 50), line.strip(), font=font_medium, fill=(220, 220, 220))
    
    # 主题标签
    if analysis["主题"]:
        theme_map = {
            "product_launch": "🚀 产品发布",
            "innovation": "💡 技术创新", 
            "business": "💼 商业动态",
            "security": "🔒 安全隐私"
        }
        theme_text = theme_map.get(analysis["主题"], "📱 科技资讯")
        draw.text((W-200, H-120), theme_text, font=font_small, fill=(255, 255, 255, 200))
    
    # 保存
    final_img = img.convert('RGB')
    final_img.save(output_path, quality=95, optimize=True)
    return True

def main():
    """主函数"""
    print("🚀 启动智能新闻图片生成器...")
    
    news_json = latest("output/news/*.json")
    if not news_json:
        print("❌ 未找到新闻数据")
        return
    
    with open(news_json, "r", encoding="utf-8") as f:
        items = json.load(f)
    
    if not items:
        print("❌ 新闻数据为空")
        return
    
    os.makedirs("assets/smart_generated", exist_ok=True)
    
    print(f"📰 处理 {len(items)} 条新闻...")
    
    success_count = 0
    for i, item in enumerate(items):
        title = item.get("title", "")
        summary = item.get("summary", "")
        source = item.get("source", "")
        
        if not title:
            continue
        
        filename = f"smart_news_{i+1}_{hashlib.md5(title.encode()).hexdigest()[:8]}.jpg"
        output_path = f"assets/smart_generated/{filename}"
        
        if create_smart_news_image(title, summary, source, output_path):
            item["image_path"] = output_path
            success_count += 1
            print(f"  ✅ 生成成功: {filename}")
        else:
            item["image_path"] = "assets/placeholder.jpg"
    
    # 保存更新的数据
    with open(news_json, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成！成功生成 {success_count}/{len(items)} 张智能图片")

if __name__ == "__main__":
    main()
