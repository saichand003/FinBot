"""Business / finance / tech news via RSS feeds."""
import time

import feedparser

import config
import db


def crawl_news():
    rows = []
    for source, url in config.NEWS_FEEDS.items():
        try:
            feed = feedparser.parse(url, agent=config.USER_AGENT)
            for e in feed.entries[:30]:
                rows.append({
                    "source": source,
                    "title": e.get("title", ""),
                    "url": e.get("link", ""),
                    "published": e.get("published", e.get("updated", "")),
                    "summary": (e.get("summary", "") or "")[:1000],
                })
        except Exception as ex:
            print(f"[news] {source} failed: {ex}")
        time.sleep(config.CRAWL_DELAY_SECONDS)
    n = db.insert_many("news", rows)
    print(f"[news] {n} new articles stored")
    return n
