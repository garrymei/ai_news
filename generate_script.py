#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, glob, datetime
from dateutil.tz import tzlocal

def latest(path):
    files = sorted(glob.glob(path), reverse=True)
    return files[0] if files else ""

def get_today_str():
    tz = tzlocal()
    now = datetime.datetime.now(tz)
    return now.astimezone().strftime("%Y-%m-%d")

def main():
    j = latest("output/news/*.json")
    if not j:
        print("no news json found"); return
    with open(j, "r", encoding="utf-8") as f:
        items = json.load(f)

    date_str = get_today_str()
    lines = []
    lines.append(f"大家好，这里是每日AI速览，今天是 {date_str}。我们用一分钟带你了解AI圈要闻。")
    for i, it in enumerate(items, 1):
        title = it.get("title","").strip()
        summ = it.get("summary","").strip()
        src  = it.get("source","")
        lines.append(f"{i}）【{src}】{title}。简要：{summ}。")
    lines.append("以上就是今天的AI要闻。想看更详细的内容，欢迎在评论区留言，我们下期见。")

    out = f"output/text/{date_str}.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] script -> %s" % out)

if __name__ == "__main__":
    main()
