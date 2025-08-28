#!/usr/bin/env bash
# AI新闻智能视频生成工作流
# 集成语义图片生成功能

set -e

echo "🚀 启动AI新闻智能视频生成工作流..."
echo "日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 创建必要目录
mkdir -p output/news output/text output/audio output/video assets/smart_generated

echo "📰 [1/5] 抓取新闻..."
python3 fetch_news.py

echo ""
echo "🎨 [2/5] 智能图片生成 (根据新闻内容语义分析)..."
python3 smart_image_generator.py

echo ""
echo "📝 [3/5] 生成文案..."
python3 generate_script.py

echo ""
echo "🎵 [4/5] 合成中文旁白..."
python3 generate_audio.py

echo ""
echo "🎬 [5/5] 合成智能视频..."
python3 generate_video.py

echo ""
echo "✅ 工作流完成！"
echo ""
echo "📋 输出文件:"
echo "   📰 新闻数据: output/news/$(date '+%Y-%m-%d').json"
echo "   📝 文案内容: output/text/$(date '+%Y-%m-%d').txt"
echo "   🎵 音频文件: output/audio/$(date '+%Y-%m-%d').mp3"
echo "   🎬 智能视频: output/video/$(date '+%Y-%m-%d').mp4"
echo ""
echo "🎨 智能生成的图片:"
if [ -d "assets/smart_generated" ]; then
    ls -la assets/smart_generated/*.jpg 2>/dev/null || echo "   (无图片文件)"
else
    echo "   (未生成图片)"
fi

echo ""
echo "📊 视频信息:"
if [ -f "output/video/$(date '+%Y-%m-%d').mp4" ]; then
    VIDEO_FILE="output/video/$(date '+%Y-%m-%d').mp4"
    VIDEO_SIZE=$(wc -c < "$VIDEO_FILE" | tr -d ' ')
    echo "   文件大小: $VIDEO_SIZE bytes ($((VIDEO_SIZE/1024)) KB)"
    echo "   文件路径: $VIDEO_FILE"
else
    echo "   ❌ 视频文件未生成"
fi

echo ""
echo "🎉 全部完成！智能AI新闻视频已生成，包含语义相关的专业图片内容。"
