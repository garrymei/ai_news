#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, glob, datetime
from gtts import gTTS
from dateutil.tz import tzlocal

def latest(path):
    files = sorted(glob.glob(path), reverse=True)
    return files[0] if files else ""

def get_today_str():
    tz = tzlocal()
    now = datetime.datetime.now(tz)
    return now.astimezone().strftime("%Y-%m-%d")

def main():
    t = latest("output/text/*.txt")
    if not t:
        print("no txt found"); return
    with open(t, "r", encoding="utf-8") as f:
        text = f.read()

    tts = gTTS(text=text, lang="zh-CN")
    date_str = get_today_str()
    out = f"output/audio/{date_str}.mp3"
    tts.save(out)
    print(f"[OK] audio -> %s" % out)

if __name__ == "__main__":
    main()
