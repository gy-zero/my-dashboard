import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser

GOOGLE_NEWS_INTL = "https://news.google.com/rss/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JYcG9MVlJYR2dKVVZ5Z0FQAQ?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
GOOGLE_NEWS_TECH = "https://news.google.com/rss/topics/CAAqLAgKIiZDQkFTRmdvSkwyMHZNR1ptZHpWbUVnVjZhQzFVVnhvQ1ZGY29BQVAB?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
GOOGLE_NEWS_USA = "https://news.google.com/rss/search?q=%E7%BE%8E%E5%9C%8B&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
GOOGLE_NEWS_TAIWAN = "https://news.google.com/rss/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRFptTXpJU0JYcG9MVlJYS0FBUAE?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
GOOGLE_NEWS_HEALTH = "https://news.google.com/rss/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNR3QwTlRFU0JYcG9MVlJYS0FBUAE?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

WORLDJOURNAL_AI_URL = "https://www.worldjournal.com/search/tagging/8877/AI"

UDN_GLOBAL_URL = "https://global.udn.com/global_vision/index"
KOC_FEED = "https://www.koc.com.tw/feed"
FM_MAIN = "https://frequentmiler.com/feed/"
FM_QUICK = "https://frequentmiler.com/category/quick-deals/feed/"

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

REQUEST_TIMEOUT = 20
MAX_RETRIES = 3
BACKOFF_SCHEDULE = [1.5, 3, 6]
NEWS_JSON_PATH = "news.json"

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def is_retryable_http_error(code):
    return code in (408, 425, 429, 500, 502, 503, 504)

def request_with_retry(url, decode_text=False, timeout=REQUEST_TIMEOUT):
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers=BROWSER_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if decode_text:
                    charset = resp.headers.get_content_charset() or "utf-8"
                    return 
