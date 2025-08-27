#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, json, time, hashlib, random, datetime
from urllib.parse import urljoin
import requests, feedparser
from bs4 import BeautifulSoup
from newspaper import Article
from dateutil.tz import tzlocal
from pathlib import Path
import yaml

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"}

def md5(s: str) -> str:
    import hashlib
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def get_today_str():
    tz = tzlocal()
    now = datetime.datetime.now(tz)
    return now.astimezone().strftime("%Y-%m-%d")

def ensure_dirs():
    for d in ["output/news", "assets/images"]:
        Path(d).mkdir(parents=True, exist_ok=True)

def download_image(url, out_dir="assets/images"):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        resp.raise_for_status()
        ext = ".jpg"
        ct = resp.headers.get("Content-Type", "")
        if "png" in ct: ext = ".png"
        name = md5(url) + ext
        path = os.path.join(out_dir, name)
        with open(path, "wb") as f:
            f.write(resp.content)
        return path
    except Exception:
        return ""

def extract_first_image(soup, base_url):
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return urljoin(base_url, og["content"])
    img = soup.select_one("article img, .post-content img, .entry-content img, .content img, img")
    if img and img.get("src"):
        return urljoin(base_url, img["src"])
    return ""

def parse_article(url, selectors=None):
    try:
        art = Article(url)
        art.download()
        art.parse()
        text = art.text.strip()
        title = art.title.strip() if art.title else ""
        top_img = art.top_image or ""
        if not top_img:
            html = requests.get(url, headers=HEADERS, timeout=12).text
            soup = BeautifulSoup(html, "lxml")
            top_img = extract_first_image(soup, url)
        return title, text, top_img
    except Exception:
        pass
    try:
        html = requests.get(url, headers=HEADERS, timeout=12).text
        soup = BeautifulSoup(html, "lxml")
        title = ""
        body = ""
        img = ""
        if selectors:
            if "title" in selectors:
                el = soup.select_one(selectors["title"])
                if el: title = el.get_text(strip=True)
            if "body" in selectors:
                el = soup.select_one(selectors["body"])
                if el: body = el.get_text(separator="\n", strip=True)
            if "image" in selectors:
                el = soup.select_one(selectors["image"])
                if el and el.get("src"): img = urljoin(url, el.get("src"))
        if not img:
            img = extract_first_image(soup, url)
        return title, body, img
    except Exception:
        return "", "", ""

def pick_links_by_selectors(list_url, selectors, limit):
    links = []
    try:
        html = requests.get(list_url, headers=HEADERS, timeout=12).text
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select(selectors["article_link"])[:limit*4]:
            href = a.get("href")
            if not href: continue
            links.append(urljoin(list_url, href))
    except Exception:
        pass
    uniq, seen = [], set()
    for u in links:
        if u not in seen:
            uniq.append(u); seen.add(u)
    return uniq[:limit]

def summarize_zh(text, max_sent=3):
    try:
        from snownlp import SnowNLP
        s = SnowNLP(text)
        sents = s.summary(max_sent)
        if isinstance(sents, list):
            return "；".join(sents)
        return sents
    except Exception:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        core = " ".join(paragraphs)[:600]
        return core

def main():
    ensure_dirs()
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    items = []
    for src in cfg.get("sources", []):
        name = src.get("name")
        rss = src.get("rss", "").strip()
        url = src.get("url", "").strip()
        limit = int(src.get("articles_per_day", 2))
        selectors = src.get("selectors", {}) or {}

        links = []
        if rss:
            try:
                feed = feedparser.parse(rss)
                for e in feed.entries[:limit*2]:
                    link = e.get("link")
                    if link: links.append(link)
            except Exception:
                pass
        elif url and selectors:
            links = pick_links_by_selectors(url, selectors, limit)

        uniq, seen = [], set()
        for u in links:
            if u not in seen:
                uniq.append(u); seen.add(u)

        for link in uniq[:limit]:
            title, body, img = parse_article(link, selectors)
            if not (title and body):
                continue
            brief = summarize_zh(body, 3)
            img_path = download_image(img) if img else ""
            items.append({
                "source": name,
                "url": link,
                "title": title,
                "summary": brief,
                "image_path": img_path,
            })
            time.sleep(random.uniform(0.5, 1.2))

    today = get_today_str()
    out = f"output/news/{today}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved %d items -> %s" % (len(items), out))

if __name__ == "__main__":
    main()
