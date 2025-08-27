#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, glob, datetime
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
from PIL import Image, ImageFont, ImageDraw
from dateutil.tz import tzlocal

W, H = 1080, 1920  # 竖屏
FONT = os.getenv("CJK_FONT_PATH", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")

def latest(path):
    files = sorted(glob.glob(path), reverse=True)
    return files[0] if files else ""

def get_today_str():
    tz = tzlocal()
    now = datetime.datetime.now(tz)
    return now.astimezone().strftime("%Y-%m-%d")

def make_slide(img_path, title, summary, duration=4.0):
    if not img_path or not os.path.exists(img_path):
        bg = Image.new("RGB", (W, H), (18,18,18))
    else:
        im = Image.open(img_path).convert("RGB")
        if im.width != W:
            im = im.resize((W, int(im.height * W / im.width)))
        if im.height < H:
            bg = Image.new("RGB", (W,H), (18,18,18))
            y = (H - im.height) // 2
            bg.paste(im, (0,y))
        else:
            top = (im.height - H)//2
            bg = im.crop((0, top, W, top+H))

    draw = ImageDraw.Draw(bg)
    try:
        font_title = ImageFont.truetype(FONT, 54)
        font_body  = ImageFont.truetype(FONT, 40)
    except:
        font_title = ImageFont.load_default()
        font_body  = ImageFont.load_default()

    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rectangle([(0, int(H*0.55)), (W, H)], fill=(0,0,0,150))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(bg)

    margin = 60
    draw.text((margin, int(H*0.58)), title[:80], font=font_title, fill=(255,255,255,255))
    draw.text((margin, int(H*0.58)+90), summary[:180], font=font_body, fill=(220,220,220,255))
    temp = "temp_slide.jpg"
    bg.convert("RGB").save(temp, quality=92)
    clip = ImageClip(temp).set_duration(duration)
    return clip

def main():
    news_json = latest("output/news/*.json")
    audio_mp3 = latest("output/audio/*.mp3")
    if not (news_json and audio_mp3):
        print("missing inputs"); return
    with open(news_json, "r", encoding="utf-8") as f:
        items = json.load(f)

    n = max(1, len(items))
    audio = AudioFileClip(audio_mp3)
    total = max(12, audio.duration)  # 至少 12 秒
    per = total / n

    clips = [make_slide(it.get("image_path",""), it.get("title",""), it.get("summary",""), per) for it in items]
    video = concatenate_videoclips(clips, method="compose").with_audio(audio)
    date_str = get_today_str()
    out = f"output/video/{date_str}.mp4"
    video.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", threads=4, preset="medium")
    print(f"[OK] video -> %s" % out)

if __name__ == "__main__":
    main()
