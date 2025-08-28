#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级AI新闻图片生成器
支持多种图片生成方案：MCP、在线API、本地生成
"""
import os, json, glob, datetime, hashlib, time
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random, requests
from dateutil.tz import tzlocal
import subprocess
import base64
from io import BytesIO

# 配置
W, H = 1080, 1920  # 竖屏尺寸
FONT_PATH = "/System/Library/Fonts/Hiragino Sans GB.ttc"

def latest(path):
    files = sorted(glob.glob(path), reverse=True)
    return files[0] if files else ""

def get_today_str():
    tz = tzlocal()
    now = datetime.datetime.now(tz)
    return now.astimezone().strftime("%Y-%m-%d")

def translate_to_english_prompt(chinese_text):
    """将中文新闻转换为英文图片生成提示词"""
    # 简单的关键词映射
    keyword_map = {
        "OpenAI": "OpenAI artificial intelligence",
        "GPT": "GPT language model technology",
        "Anthropic": "Anthropic AI company",
        "Claude": "Claude AI assistant",
        "机器人": "advanced robotics technology",
        "人工智能": "artificial intelligence AI",
        "MIT": "MIT university research laboratory",
        "导航": "navigation autonomous system",
        "算法": "algorithm computer science",
        "深度学习": "deep learning neural network",
        "数据": "data analytics technology",
        "科技": "technology innovation",
        "研发": "research development laboratory",
        "突破": "breakthrough innovation",
        "发布": "product launch announcement"
    }
    
    # 构建英文提示词
    prompt_parts = []
    for chinese, english in keyword_map.items():
        if chinese in chinese_text:
            prompt_parts.append(english)
    
    if not prompt_parts:
        prompt_parts = ["artificial intelligence", "technology innovation"]
    
    # 添加通用风格描述
    style_keywords = [
        "professional", "modern", "high-tech", "blue color scheme",
        "digital graphics", "clean design", "corporate style",
        "technology background", "futuristic", "sleek interface"
    ]
    
    prompt = ", ".join(prompt_parts[:3] + style_keywords[:4])
    return prompt

def generate_with_stability_api(prompt, output_path):
    """使用Stability AI API生成图片 (需要API key)"""
    try:
        api_key = os.getenv("STABILITY_API_KEY")
        if not api_key:
            return False
            
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": 1920,
            "width": 1080,
            "samples": 1,
            "steps": 30,
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if data["artifacts"]:
                image_data = base64.b64decode(data["artifacts"][0]["base64"])
                with open(output_path, "wb") as f:
                    f.write(image_data)
                return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ Stability API错误: {e}")
        return False

def generate_with_local_diffusion(prompt, output_path):
    """使用本地Stable Diffusion生成图片 (如果已安装)"""
    try:
        # 检查是否安装了diffusers
        import torch
        from diffusers import StableDiffusionPipeline
        
        # 加载模型 (首次运行会下载，需要时间)
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
        
        # 生成图片
        image = pipe(
            prompt,
            height=1920,
            width=1080,
            num_inference_steps=20,
            guidance_scale=7.5
        ).images[0]
        
        image.save(output_path)
        return True
        
    except ImportError:
        print("  ⚠️ 未安装diffusers库，跳过本地Stable Diffusion")
        return False
    except Exception as e:
        print(f"  ❌ 本地Diffusion错误: {e}")
        return False

def create_enhanced_local_image(title, summary, source, output_path):
    """增强版本地图片生成"""
    # 获取主题色彩
    content = (title + " " + summary).lower()
    
    # 更丰富的主题色彩方案
    if "openai" in content or "gpt" in content:
        colors = [(74, 222, 128), (34, 197, 94)]  # 绿色 (OpenAI主题色)
    elif "anthropic" in content or "claude" in content:
        colors = [(251, 146, 60), (249, 115, 22)]  # 橙色 (Anthropic主题色)
    elif "机器人" in content or "robot" in content:
        colors = [(168, 85, 247), (139, 69, 219)]  # 紫色
    elif "mit" in content or "研究" in content:
        colors = [(59, 130, 246), (37, 99, 235)]  # 蓝色
    else:
        colors = [(14, 165, 233), (2, 132, 199)]  # 默认蓝色
    
    # 创建渐变背景
    img = Image.new('RGB', (W, H), colors[0])
    
    # 创建复杂渐变
    for y in range(H):
        for x in range(W):
            # 径向渐变效果
            center_x, center_y = W//3, H//4
            distance = ((x - center_x)**2 + (y - center_y)**2)**0.5
            max_distance = (W**2 + H**2)**0.5
            ratio = min(distance / max_distance * 2, 1.0)
            
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            
            img.putpixel((x, y), (r, g, b))
    
    # 添加科技感图案
    draw = ImageDraw.Draw(img)
    
    # 添加几何图形
    for i in range(8):
        x = random.randint(0, W)
        y = random.randint(0, H//2)
        size = random.randint(30, 120)
        alpha = random.randint(10, 40)
        
        # 创建半透明图层
        overlay = Image.new('RGBA', (W, H), (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # 随机几何形状
        shape_type = random.choice(['circle', 'rectangle', 'triangle'])
        if shape_type == 'circle':
            overlay_draw.ellipse([x, y, x+size, y+size], fill=(255, 255, 255, alpha))
        elif shape_type == 'rectangle':
            overlay_draw.rectangle([x, y, x+size, y+size//2], fill=(255, 255, 255, alpha))
        
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # 添加网格线条
    draw = ImageDraw.Draw(img)
    grid_color = (255, 255, 255, 30)
    
    # 垂直线
    for x in range(0, W, 80):
        draw.line([(x, 0), (x, H//2)], fill=grid_color, width=1)
    
    # 水平线  
    for y in range(0, H//2, 80):
        draw.line([(0, y), (W, y)], fill=grid_color, width=1)
    
    # 转换为RGBA添加文字层
    img = img.convert('RGBA')
    
    # 添加文字背景
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 顶部品牌区域
    draw.rectangle([(0, 0), (W, 180)], fill=(0, 0, 0, 100))
    
    # 底部文字区域
    draw.rectangle([(0, H*2//3), (W, H)], fill=(0, 0, 0, 140))
    
    img = Image.alpha_composite(img, overlay)
    
    # 添加文字
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        font_large = ImageFont.truetype(FONT_PATH, 64)
        font_medium = ImageFont.truetype(FONT_PATH, 42)
        font_small = ImageFont.truetype(FONT_PATH, 32)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # 品牌标识
    draw.text((60, 60), "AI科技资讯", font=font_medium, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0,0,0))
    draw.text((60, 120), f"📰 {source}", font=font_small, fill=(200, 200, 200))
    
    # 主标题处理
    y_pos = H*2//3 + 60
    title_lines = []
    
    # 智能换行
    if len(title) > 16:
        # 寻找合适的断点
        break_chars = "，。！？、"
        best_break = len(title) // 2
        
        for i in range(len(title)//2 - 5, len(title)//2 + 5):
            if i < len(title) and title[i] in break_chars:
                best_break = i + 1
                break
        
        title_lines = [title[:best_break].strip(), title[best_break:].strip()]
    else:
        title_lines = [title]
    
    # 绘制标题
    for i, line in enumerate(title_lines):
        if line:
            draw.text((60, y_pos + i * 85), line, font=font_large, fill=(255, 255, 255), 
                     stroke_width=1, stroke_fill=(0,0,0))
    
    # 摘要
    y_pos += len(title_lines) * 85 + 30
    summary_text = summary[:80] + "..." if len(summary) > 80 else summary
    draw.text((60, y_pos), summary_text, font=font_medium, fill=(220, 220, 220))
    
    # 添加装饰元素
    draw.ellipse([(W-150, 50), (W-50, 150)], outline=(255, 255, 255, 100), width=3)
    draw.text((W-120, 90), "AI", font=font_medium, fill=(255, 255, 255, 150))
    
    # 保存
    final_img = img.convert('RGB')
    final_img.save(output_path, quality=95, optimize=True)
    return True

def generate_news_image_advanced(title, summary, source, output_path):
    """高级图片生成，尝试多种方案"""
    print(f"  🎨 生成图片: {title[:30]}...")
    
    # 方案1: 尝试在线API (如果配置了)
    english_prompt = translate_to_english_prompt(title + " " + summary)
    print(f"  📝 英文提示词: {english_prompt}")
    
    if generate_with_stability_api(english_prompt, output_path):
        print(f"  ✅ Stability AI生成成功")
        return True
    
    # 方案2: 尝试本地Stable Diffusion
    if generate_with_local_diffusion(english_prompt, output_path):
        print(f"  ✅ 本地Diffusion生成成功")
        return True
    
    # 方案3: 增强版本地图片生成
    if create_enhanced_local_image(title, summary, source, output_path):
        print(f"  ✅ 增强本地生成成功")
        return True
    
    print(f"  ❌ 所有图片生成方案失败")
    return False

def main():
    """主函数"""
    print("🚀 启动高级AI新闻图片生成器...")
    
    # 获取新闻数据
    news_json = latest("output/news/*.json")
    if not news_json:
        print("❌ 未找到新闻数据")
        return
    
    with open(news_json, "r", encoding="utf-8") as f:
        items = json.load(f)
    
    if not items:
        print("❌ 新闻数据为空")
        return
    
    # 确保输出目录存在
    os.makedirs("assets/ai_generated_images", exist_ok=True)
    
    print(f"📰 处理 {len(items)} 条新闻...")
    
    # 生成图片
    success_count = 0
    for i, item in enumerate(items):
        title = item.get("title", "")
        summary = item.get("summary", "")
        source = item.get("source", "")
        
        if not title:
            continue
        
        # 生成文件名
        filename = f"ai_news_{i+1}_{hashlib.md5(title.encode()).hexdigest()[:8]}.jpg"
        output_path = f"assets/ai_generated_images/{filename}"
        
        if generate_news_image_advanced(title, summary, source, output_path):
            item["image_path"] = output_path
            success_count += 1
        else:
            # 备用：使用占位图片
            item["image_path"] = "assets/placeholder.jpg"
        
        time.sleep(1)  # 避免API限制
    
    # 保存更新的新闻数据
    with open(news_json, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成！成功生成 {success_count}/{len(items)} 张图片")
    print(f"📁 图片保存在: assets/ai_generated_images/")

if __name__ == "__main__":
    main()
