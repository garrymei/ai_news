#!/usr/bin/env bash
set -e
mkdir -p output/news output/text output/audio output/video assets/images
echo "[1/4] 抓取新闻…"; python3 fetch_news.py
echo "[2/4] 生成文案…"; python3 generate_script.py
echo "[3/4] 合成中文旁白…"; python3 generate_audio.py
echo "[4/4] 合成视频…"; python3 generate_video.py
echo "完成！请查看 output/video/*.mp4"
