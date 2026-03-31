# -*- coding: utf-8 -*-
"""
Bing News 新闻爬虫
支持 Selenium 渲染动态页面
"""

import os
import json
import re
import time
import logging
import sys
from glob import glob
import requests
import urllib3
from urllib.parse import urlparse, parse_qs, unquote, quote
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup

# 禁用 webdriver_manager 网络请求
os.environ['WDM_LOG'] = '0'
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_LOCAL'] = '1'
os.environ['WDM_SSL_VERIFY'] = '0'
os.environ['WDM_OFFLINE'] = '1'
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'
# 禁用 selenium-manager 自动下载
os.environ['SE_MANAGER_DISABLED'] = '1'
for _name in ['WDM', 'webdriver_manager', 'webdriver_manager.core', 'urllib3', 'selenium.webdriver.common.selenium_manager']:
    logging.getLogger(_name).setLevel(logging.CRITICAL)
    logging.getLogger(_name).propagate = False
    logging.getLogger(_name).disabled = True

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 检查 Selenium 是否可用
HAS_SELENIUM = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    pass


class BingNewsCrawler:
    # 使用国际版 www.bing.com（cn.bing.com 不支持新闻搜索）
    SEARCH_URL = "https://www.bing.com/news/search"

    def __init__(self, keyword="synopsys", keywords=None):
        self.keywords = self._build_keywords(keywords if keywords else [keyword])
        self.keyword = self.keywords[0] if self.keywords else keyword
        self.active_keywords = list(self.keywords)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.7,zh;q=0.6',
            'Referer': 'https://www.bing.com/',
        }
        self.request_timeout = 6
        self.supplement_timeout = 4
        self.max_web_candidates = 3

    def _build_keywords(self, keywords):
        vals = []
        for k in (keywords or []):
            s = str(k).strip()
            if not s:
                continue
            if s.lower() in [x.lower() for x in vals]:
                continue
            vals.append(s)
        return vals or ['EDA']

    def _find_local_chromedriver(self):
        """查找本地 chromedriver"""
        roots = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.wdm', 'drivers', 'chromedriver'),
            os.path.join(os.getcwd(), '.wdm', 'drivers', 'chromedriver'),
            os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver'),
        ]
        candidates = []
        for root in roots:
            if not os.path.isdir(root):
                continue
            candidates.extend(glob(os.path.join(root, '**', 'chromedriver.exe'), recursive=True))
            candidates.extend(glob(os.path.join(root, '**', 'chromedriver'), recursive=True))
        candidates = [p for p in candidates if os.path.isfile(p)]
        if not candidates:
            return ''
        candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return candidates[0]

    def _is_keyword_relevant(self, text):
        if not text:
            return False
        t = (text or '').lower()
        keywords = [k.strip().lower() for k in (self.active_keywords or [self.keyword]) if str(k).strip()]
        if not keywords:
            return True
        for k in keywords:
            if k and k in t:
                return True
        if 'eda' in keywords:
            related_tokens = [
                'synopsys', 'cadence', 'siemens',
                '电子设计自动化', 'chip design', 'semiconductor design',
                'ic design', 'verification', 'logic synthesis'
            ]
            if any(tok in t for tok in related_tokens):
                return True
        return any(k in t for k in ['synopsys', 'cadence', 'siemens'] if k in keywords)

    def _parse_bing_pubdate(self, pub_date):
        if not pub_date:
            return ''
        try:
            dt = parsedate_to_datetime(pub_date)
            if dt is None:
                return ''
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return ''

    def _parse_bing_time_text(self, time_text):
        if not time_text:
            return ''
        txt = time_text.strip().lower()
        now = datetime.now()
        m = re.search(r'(\d+)\s*分钟前', txt)
        if m:
            return (now - timedelta(minutes=int(m.group(1)))).strftime('%Y-%m-%d')
        m = re.search(r'(\d+)\s*小时前', txt)
        if m:
            return (now - timedelta(hours=int(m.group(1)))).strftime('%Y-%m-%d')
        m = re.search(r'(\d+)\s*天前', txt)
        if m:
            return (now - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d')
        m = re.search(r'(\d+)\s*m\b', txt)
        if m:
            return (now - timedelta(minutes=int(m.group(1)))).strftime('%Y-%m-%d')
        m = re.search(r'(\d+)\s*h\b', txt)
        if m:
            return (now - timedelta(hours=int(m.group(1)))).strftime('%Y-%m-%d')
        m = re.search(r'(\d+)\s*d\b', txt)
        if m:
            return (now - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d')
        m = re.search(r'(\d+)\s*(minute|minutes|hour|hours|day|days)\s*ago', txt)
        if m:
            n = int(m.group(1))
            unit = m.group(2)
            if 'minute' in unit:
                return (now - timedelta(minutes=n)).strftime('%Y-%m-%d')
            if 'hour' in unit:
                return (now - timedelta(hours=n)).strftime('%Y-%m-%d')
            return (now - timedelta(days=n)).strftime('%Y-%m-%d')
        m = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', txt)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        m = re.search(r'(\d{1,2})[-/](\d{1,2})', txt)
        if m:
            return f"{now.year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
        return ''

    def _unwrap_bing_link(self, link):
        if not link:
            return ''
        try:
            parsed = urlparse(link)
            qs = parse_qs(parsed.query)
            real = qs.get('url', [''])[0]
            if real:
                return unquote(real)
            return link
        except Exception:
            return link

    def _is_real_news_link(self, link):
        u = (link or '').strip().lower()
        if not u.startswith('http'):
            return False
        if 'bing.com/news/search' in u:
            return False
        if 'bing.com/news/infinitescrollajax' in u:
            return False
        if 'javascript:' in u:
            return False
        return True

    def _is_news_like_link(self, link):
        u = (link or '').strip().lower()
        if not u.startswith('http'):
            return False
        if 'bing.com/news/search' in u or 'bing.com/news/infinitescrollajax' in u:
            return False
        if 'wikipedia.org' in u:
            return False
        bad_domains = ['zhihu.com', 'tieba.baidu.com', 'weibo.com', 'x.com', 'twitter.com', 'reddit.com']
        if any(d in u for d in bad_domains):
            return False
        try:
            p = urlparse(u)
            host = (p.netloc or '').lower()
            path = (p.path or '').lower()
        except Exception:
            return False
        if host.endswith('synopsys.com'):
            if host == 'news.synopsys.com':
                return ('news-release' in path) or ('/article' in path)
            return False
        if host == 'investors.ansys.com':
            return 'news-release-details' in path
        good_domains = [
            'reuters.com', 'cnbc.com', 'bizjournals.com', 'benzinga.com', 'yahoo.com',
            'marketwatch.com', 'fool.com', 'investing.com', 'seekingalpha.com',
            'msn.com', 'nasdaq.com', 'finance.yahoo.com', 'bloomberg.com'
        ]
        if any(d in host for d in good_domains):
            if path in ['', '/']:
                return False
            return True
        if '/news/' in path or '/article/' in path or '/story/' in path:
            return True
        return False

    def _is_news_title(self, title):
        t = (title or '').strip().lower()
        if not t:
            return False
        bad_tokens = ['newsroom', 'news releases', 'about us', 'working at', 'wikipedia']
        return not any(tok in t for tok in bad_tokens)

    def _build_page_url(self, page_num):
        first = (page_num - 1) * 11 + 1
        query = quote(f"{self.keyword}")
        if page_num <= 1:
            return f"{self.SEARCH_URL}?format=rss&q={query}&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR"
        return f"{self.SEARCH_URL}?format=rss&q={query}&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR&first={first}"

    def _build_rss_candidate_urls(self, page_num):
        first = (page_num - 1) * 11 + 1
        q = quote(f"{self.keyword}")
        base = [
            f"{self.SEARCH_URL}?format=rss&q={q}&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR",
            f"{self.SEARCH_URL}?format=rss&q={q}&setmkt=en-US&setlang=en-US&cc=US&qft=sortbydate%3d%221%22&form=YFNR",
            f"{self.SEARCH_URL}?format=rss&q={q}&mkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR",
            f"{self.SEARCH_URL}?cc=us&mkt=en-US&setlang=en-US&q={q}&format=rss",
            f"{self.SEARCH_URL}?ensearch=1&q={q}&format=rss",
            f"https://www.bing.com/search?q={q}&format=rss",
        ]
        if page_num <= 1:
            return base
        return [u + f"&first={first}" for u in base]

    def _build_html_candidate_urls(self, page_num):
        first = (page_num - 1) * 11 + 1
        q = quote(f"{self.keyword}")
        base = [
            f"https://www.bing.com/news/infinitescrollajax?q={q}&qft=sortbydate%3d%221%22&form=YFNR",
            f"{self.SEARCH_URL}?q={q}&qft=sortbydate%3d%221%22&form=YFNR&setmkt=en-US&setlang=en-US",
            f"{self.SEARCH_URL}?q={q}&qft=sortbydate%3d%221%22&form=YFNR",
            f"https://www.bing.com/news/search?q={q}&qft=sortbydate%3d%221%22&form=YFNR&setmkt=en-US&setlang=en-US",
            f"https://www.bing.com/news/search?q={q}&qft=sortbydate%3d%221%22&form=YFNR",
        ]
        if page_num <= 1:
            return base
        return [u + f"&first={first}" for u in base]

    def _build_web_rss_candidate_urls(self):
        queries = [
            f"{self.keyword} reuters",
            f"{self.keyword} cnbc",
            f"{self.keyword} bloomberg",
            f"{self.keyword} marketwatch",
            f"{self.keyword} seekingalpha",
        ]
        urls = []
        for q in queries:
            qq = quote(q)
            urls.append(f"https://www.bing.com/search?q={qq}&format=rss&ensearch=1&setlang=en-US&mkt=en-US&cc=US")
            urls.append(f"https://www.bing.com/search?q={qq}&format=rss&ensearch=1&setlang=en-US&mkt=en-US")
        return urls

    def _build_web_search_candidate_urls(self):
        queries = [
            f"{self.keyword} site:reuters.com",
            f"{self.keyword} site:cnbc.com",
            f"{self.keyword} site:bloomberg.com",
            f"{self.keyword} site:marketwatch.com",
            f"{self.keyword} site:seekingalpha.com",
            f"{self.keyword} site:benzinga.com",
        ]
        return [f"https://www.bing.com/search?q={quote(q)}&setlang=en-US&mkt=en-US&cc=US" for q in queries]

    def _looks_like_rss(self, text):
        s = (text or '')[:240].lower()
        return ('<rss' in s) or ('<?xml' in s and '<channel' in (text or '')[:800].lower())

    def _is_bing_news_rss(self, text):
        s = (text or '')[:1200].lower()
        return 'bingnews' in s or 'news/search?format=rss' in s

    def _fetch_rss_text(self, page_num):
        q = quote(f"{self.keyword}")
        first = (page_num - 1) * 11 + 1
        url = f"https://www.bing.com/news/search?format=rss&q={q}&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR&first={first}"
        rss_headers = {
            'User-Agent': self.headers['User-Agent'],
            'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.bing.com/news/search'
        }
        try:
            resp = requests.get(
                url,
                headers=rss_headers,
                timeout=self.request_timeout,
                verify=False,
                allow_redirects=True,
                proxies={'http': None, 'https': None}
            )
            txt = (resp.text or '')
            if self._looks_like_rss(txt):
                return txt
        except Exception:
            pass
        return ''

    def _fetch_web_rss_text(self):
        for url in self._build_web_rss_candidate_urls():
            try:
                resp = requests.get(
                    url,
                    timeout=self.request_timeout,
                    verify=False,
                    allow_redirects=True,
                    proxies={'http': None, 'https': None}
                )
                txt = (resp.text or '')
                if not self._looks_like_rss(txt):
                    continue
                low = txt.lower()
                if any(d in low for d in ['reuters.com', 'cnbc.com', 'bloomberg.com', 'marketwatch.com', 'seekingalpha.com']):
                    return txt
            except Exception:
                continue
        return ''

    def _fetch_web_rss_news(self, cutoff_date):
        all_news = []
        for url in self._build_web_rss_candidate_urls()[:self.max_web_candidates]:
            try:
                resp = requests.get(
                    url,
                    timeout=self.supplement_timeout,
                    verify=False,
                    allow_redirects=True,
                    proxies={'http': None, 'https': None}
                )
                txt = (resp.text or '')
                if not self._looks_like_rss(txt):
                    continue
                all_news.extend(self._extract_from_rss_text(txt, cutoff_date)[:8])
                if len(all_news) >= 8:
                    break
            except Exception:
                continue
        return all_news

    def _fetch_web_search_news(self, cutoff_date):
        today = datetime.now().strftime('%Y-%m-%d')
        out = []
        seen = set()
        for url in self._build_web_search_candidate_urls()[:self.max_web_candidates]:
            try:
                resp = requests.get(
                    url,
                    timeout=self.supplement_timeout,
                    verify=False,
                    allow_redirects=True,
                    proxies={'http': None, 'https': None}
                )
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, 'html.parser')
                for a in soup.select('li.b_algo h2 a[href]'):
                    title = a.get_text(' ', strip=True)
                    link = (a.get('href') or '').strip()
                    if not title or not link:
                        continue
                    if not self._is_news_title(title):
                        continue
                    if not self._is_keyword_relevant(title):
                        continue
                    real_link = self._unwrap_bing_link(link)
                    if not self._is_news_like_link(real_link):
                        continue
                    p = a.find_parent('li')
                    txt = p.get_text(' | ', strip=True) if p else ''
                    date = self._parse_bing_time_text(txt) or today
                    if date < cutoff_date:
                        continue
                    key = (real_link, title)
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append({
                        'title': title,
                        'link': real_link,
                        'date': date,
                        'source': 'Bing新闻',
                        'summary': txt,
                    })
                    if len(out) >= 8:
                        return out
            except Exception:
                continue
        return out

    def _fetch_html_news(self, page_num, cutoff_date):
        html_headers = {
            'User-Agent': self.headers['User-Agent'],
            'Accept': 'text/html,*/*',
            'Referer': f"https://www.bing.com/news/search?q={quote(self.keyword)}"
        }
        for _ in range(1):
            for url in self._build_html_candidate_urls(page_num)[:2]:
                try:
                    resp = requests.get(
                        url,
                        headers=html_headers,
                        timeout=self.request_timeout,
                        verify=False,
                        allow_redirects=True,
                        proxies={'http': None, 'https': None}
                    )
                    if resp.status_code != 200:
                        continue
                    page_news = self._extract_from_html_page(resp.text, cutoff_date)
                    if page_news:
                        return page_news
                except Exception:
                    continue
        return []

    def _extract_from_html_page(self, html, cutoff_date):
        soup = BeautifulSoup(html, 'html.parser')
        result = []
        seen = set()
        today = datetime.now().strftime('%Y-%m-%d')
        for a in soup.select('a[href]'):
            title = a.get_text(' ', strip=True)
            link = (a.get('href') or '').strip()
            if not title or not link:
                continue
            if link.startswith('//'):
                link = 'https:' + link
            elif link.startswith('/'):
                link = 'https://www.bing.com' + link
            if not link.startswith('http'):
                continue
            if not self._is_keyword_relevant(title):
                continue
            real_link = self._unwrap_bing_link(link)
            if not self._is_news_like_link(real_link):
                continue
            parent = a.parent if a else None
            parent_text = parent.get_text(" | ", strip=True) if parent else ''
            date = self._parse_bing_time_text(parent_text)
            if not date:
                date = today
            if date < cutoff_date:
                continue
            key = (real_link, title)
            if key in seen:
                continue
            seen.add(key)
            result.append({
                'title': title,
                'link': real_link,
                'date': date,
                'source': 'Bing新闻',
                'summary': parent_text,
            })
        return result

    def _extract_from_rss_text(self, rss_text, cutoff_date):
        if not rss_text:
            return []
        try:
            root = ET.fromstring(rss_text)
        except Exception:
            return []
        items = root.findall('./channel/item')
        page_news = []
        for item in items:
            title = (item.findtext('title') or '').strip()
            link = (item.findtext('link') or '').strip()
            pub_date = (item.findtext('pubDate') or '').strip()
            desc = (item.findtext('description') or '').strip()
            desc_text = BeautifulSoup(desc, 'html.parser').get_text(' ', strip=True)
            date = self._parse_bing_pubdate(pub_date)
            if not title or not link:
                continue
            if not self._is_news_title(title):
                continue
            if not (self._is_keyword_relevant(title) or self._is_keyword_relevant(desc)):
                continue
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            if date < cutoff_date:
                continue
            real_link = self._unwrap_bing_link(link)
            if not self._is_news_like_link(real_link):
                continue
            page_news.append({
                'title': title,
                'link': real_link,
                'date': date,
                'source': 'Bing新闻',
                'summary': desc_text,
            })
        return page_news

    def _parse_relative_time(self, time_text):
        """解析相对时间，如 '14 小时', '3小时前', '2天前', '3 days'"""
        if not time_text:
            return ''
        now = datetime.now()
        time_text = time_text.strip()
        
        # 中文格式: "X 分钟" 或 "X分钟前" 或 "X分前"
        if '分钟' in time_text or '分前' in time_text:
            return now.strftime('%Y-%m-%d')
        
        # 中文格式: "X 小时" 或 "X小时前"
        m = re.search(r'(\d+)\s*小时', time_text)
        if m:
            hours_ago = int(m.group(1))
            return (now - timedelta(hours=hours_ago)).strftime('%Y-%m-%d')
        
        if '刚刚' in time_text or '今天' in time_text:
            return now.strftime('%Y-%m-%d')
        if '昨天' in time_text:
            return (now - timedelta(days=1)).strftime('%Y-%m-%d')
        if '前天' in time_text:
            return (now - timedelta(days=2)).strftime('%Y-%m-%d')
        
        # 中文格式: "X 天" 或 "X天前"
        m = re.search(r'(\d+)\s*天', time_text)
        if m:
            days_ago = int(m.group(1))
            return (now - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # 中文格式: "X 周" 或 "X周前"
        m = re.search(r'(\d+)\s*周', time_text)
        if m:
            weeks_ago = int(m.group(1))
            return (now - timedelta(weeks=weeks_ago)).strftime('%Y-%m-%d')
        
        # 中文格式: "X 月" 或 "X月前"
        m = re.search(r'(\d+)\s*月', time_text)
        if m:
            months_ago = int(m.group(1))
            return (now - timedelta(days=months_ago*30)).strftime('%Y-%m-%d')
        
        # 英文格式: "X minutes ago", "X hours ago", "X days ago"
        m = re.search(r'(\d+)\s*(?:minute|min)', time_text, re.IGNORECASE)
        if m:
            return now.strftime('%Y-%m-%d')
        
        m = re.search(r'(\d+)\s*(?:hour|hr)', time_text, re.IGNORECASE)
        if m:
            hours_ago = int(m.group(1))
            return (now - timedelta(hours=hours_ago)).strftime('%Y-%m-%d')
        
        m = re.search(r'(\d+)\s*day', time_text, re.IGNORECASE)
        if m:
            days_ago = int(m.group(1))
            return (now - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        m = re.search(r'(\d+)\s*week', time_text, re.IGNORECASE)
        if m:
            weeks_ago = int(m.group(1))
            return (now - timedelta(weeks=weeks_ago)).strftime('%Y-%m-%d')
        
        # 尝试解析日期格式
        # YYYY-MM-DD 或 YYYY/MM/DD
        m = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', time_text)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        
        # MM/DD/YYYY 格式（Bing aria-label 常用）
        m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', time_text)
        if m:
            return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
        
        # MM-DD 格式（无年份，使用当前年）
        m = re.search(r'(\d{1,2})[-/](\d{1,2})(?!/)', time_text)
        if m:
            return f"{now.year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
        
        return ''

    def _crawl_with_selenium(self, max_pages, cutoff_date):
        """使用 Selenium 爬取动态渲染的页面"""
        if not HAS_SELENIUM:
            print("  Selenium 未安装，跳过动态渲染")
            return []
        
        all_news = []
        driver = None
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            chrome_options.add_argument('--log-level=3')
            
            # 查找本地 chromedriver
            driver_path = self._find_local_chromedriver()
            if driver_path:
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # 尝试不指定 service 直接创建
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                except Exception:
                    print("  无法创建 Chrome driver")
                    return []
            
            for page_num in range(1, max_pages + 1):
                try:
                    # Bing 新闻搜索 URL，按时间排序，使用英文版
                    first = (page_num - 1) * 10 + 1
                    url = f"{self.SEARCH_URL}?q={quote(self.keyword)}&qft=sortbydate%3d%221%22&setmkt=en-US&setlang=en-US&cc=US&ensearch=1&first={first}"
                    
                    driver.get(url)
                    time.sleep(3)  # 等待页面加载
                    
                    # 等待新闻卡片加载
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.news-card, .newsitem'))
                        )
                        time.sleep(2)  # 额外等待确保内容加载完成
                    except Exception:
                        pass
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    page_news = []
                    
                    # 方案 1: 标准新闻卡片 (.news-card)
                    for card in soup.select('.news-card'):
                        title_elem = card.select_one('a.title')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        if not title or len(title) < 5:
                            continue
                        
                        link = title_elem.get('href', '')
                        
                        # 解析真实链接
                        real_link = self._unwrap_bing_link(link)
                        if not self._is_real_news_link(real_link):
                            continue
                        if not real_link:
                            continue
                        
                        # 解析时间 - Bing 新闻卡片中的时间
                        date = ''
                        # 方式1: 使用 span 的 aria-label 属性（优先，包含精确日期如 "10/11/2025"）
                        time_span = card.select_one('.source span[aria-label]')
                        if time_span:
                            date = self._parse_relative_time(time_span.get('aria-label', ''))
                        # 方式2: 使用 .ns_sc_tm 选择器
                        if not date:
                            time_elem = card.select_one('.source .ns_sc_tm')
                            if time_elem:
                                date = self._parse_relative_time(time_elem.get_text(strip=True))
                        # 方式3: 遍历所有 span 找包含时间关键词的文本
                        if not date:
                            source_elem = card.select_one('.source')
                            if source_elem:
                                for span in source_elem.select('span'):
                                    text = span.get_text(strip=True)
                                    if text and ('小时' in text or '天' in text or '分' in text or 'hour' in text.lower() or 'day' in text.lower()):
                                        date = self._parse_relative_time(text)
                                        break
                        if not date:
                            date = datetime.now().strftime('%Y-%m-%d')
                        
                        if date < cutoff_date:
                            continue
                        
                        if not self._is_keyword_relevant(title):
                            continue
                        
                        summary = ''
                        summary_elem = card.select_one('.snippet, .snippet_text, .news-card-snippet, .body')
                        if summary_elem:
                            summary = summary_elem.get_text(' ', strip=True)
                        page_news.append({
                            'title': title,
                            'link': real_link,
                            'date': date,
                            'source': 'Bing新闻',
                            'summary': summary,
                        })
                    
                    # 方案 2: 标题链接
                    if not page_news:
                        for a in soup.select('a.title, h2 a, h3 a'):
                            title = a.get_text(strip=True)
                            if not title or len(title) < 5:
                                continue
                            link = a.get('href', '')
                            real_link = self._unwrap_bing_link(link)
                            if not self._is_real_news_link(real_link):
                                continue
                            if not real_link:
                                continue
                            if not self._is_keyword_relevant(title):
                                continue
                            page_news.append({
                                'title': title,
                                'link': real_link,
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'source': 'Bing新闻',
                                'summary': '',
                            })
                    
                    print(f"  Selenium 第 {page_num} 页: {len(page_news)} 条新闻")
                    all_news.extend(page_news)
                    
                    if not page_news:
                        break
                    
                except Exception as e:
                    print(f"  Selenium 第 {page_num} 页出错: {e}")
                    break
            
        except Exception as e:
            print(f"  Selenium 初始化失败: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
        
        return all_news

    def crawl(self, max_pages=1, days=7, min_content_length=500, keywords=None):
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        kw_list = self._build_keywords(keywords if keywords else self.keywords)
        self.active_keywords = kw_list
        print(f"\n正在爬取 Bing 新闻（关键词: {', '.join(kw_list)}，最近 {days} 天）...")

        for kw in kw_list:
            self.keyword = kw
            print(f"  抓取关键词: {kw}")
            if HAS_SELENIUM:
                selenium_news = self._crawl_with_selenium(max_pages, cutoff_date)
                all_news.extend(selenium_news)
            print("  执行 RSS/HTML 补量...")
            empty_pages = 0
            web_supplement_done = False
            for page_num in range(1, max_pages + 1):
                try:
                    page_news = []
                    rss_text = self._fetch_rss_text(page_num)
                    rss_news = self._extract_from_rss_text(rss_text, cutoff_date)
                    if rss_news:
                        page_news.extend(rss_news)
                    if len(page_news) < 3:
                        page_news.extend(self._fetch_html_news(page_num, cutoff_date))
                    if not web_supplement_done and (page_num == 1 or len(page_news) < 2):
                        web_supplement_done = True
                        page_news.extend(self._fetch_web_rss_news(cutoff_date))
                        if len(page_news) < 3:
                            page_news.extend(self._fetch_web_search_news(cutoff_date))
                    if not page_news:
                        empty_pages += 1
                        print(f"  第 {page_num} 页没有新闻")
                        if empty_pages >= 2:
                            break
                        continue
                    empty_pages = 0
                    page_count = 0
                    for news in page_news:
                        all_news.append(news)
                        page_count += 1
                    print(f"  第 {page_num} 页补量: {page_count} 条新闻")
                except Exception as e:
                    print(f"  第 {page_num} 页出错: {e}")
                    break

        unique_news = []
        seen_links = set()
        for news in all_news:
            link = news.get('link', '')
            if link and link not in seen_links:
                seen_links.add(link)
                unique_news.append(news)

        if min_content_length > 0 and unique_news:
            print(f"  正在获取新闻内容并过滤（>={min_content_length}字）...")
            filtered_news = []
            for news in unique_news:
                content = self.fetch_news_content(news['link'])
                if not content:
                    content = (news.get('summary') or '').strip()
                content_len = len(content) if content else 0
                if content_len >= min_content_length:
                    news['content'] = content
                    filtered_news.append(news)
            unique_news = filtered_news

        print(f"  共获取 {len(unique_news)} 条新闻")
        return unique_news

    def fetch_news_content(self, url):
        for attempt in range(2):
            try:
                resp = requests.get(
                    url,
                    headers={
                        'User-Agent': self.headers['User-Agent'],
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': self.headers['Accept-Language'],
                    },
                    timeout=15,
                    verify=False,
                    proxies={'http': None, 'https': None}
                )
                if resp.status_code != 200:
                    continue
                resp.encoding = resp.apparent_encoding or 'utf-8'
                soup = BeautifulSoup(resp.text, 'html.parser')
                selectors = [
                    'article',
                    '.article-content',
                    '.entry-content',
                    '.post-content',
                    '.news-content',
                    '.content',
                    'main',
                ]
                for selector in selectors:
                    content_elem = soup.select_one(selector)
                    if not content_elem:
                        continue
                    for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'header', 'footer', 'iframe']):
                        tag.decompose()
                    paragraphs = content_elem.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True) and len(p.get_text(strip=True)) > 10])
                    else:
                        content = content_elem.get_text(separator='\n', strip=True)
                    if content and len(content) > 100:
                        return content
                return ''
            except Exception:
                continue
        return ''

    def save_to_json(self, news_list, filename='bing_news.json'):
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        data = {
            '行业新闻': {
                'Bing新闻': [
                    {'title': n.get('title', ''), 'link': n.get('link', ''), 'date': n.get('date', ''), 'content': n.get('content', '')}
                    for n in news_list
                ]
            }
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"新闻已保存到: {filepath}")
        return filepath


def main():
    print("=" * 50)
    print("Bing 新闻爬虫 (关键词: EDA)")
    print("=" * 50)
    crawler = BingNewsCrawler(keyword="EDA")
    news_list = crawler.crawl(max_pages=1, days=7, min_content_length=500)
    if news_list:
        print("\n爬取结果预览：")
        for i, news in enumerate(news_list[:5], 1):
            content_len = len(news.get('content', '')) if news.get('content') else 0
            print(f"\n{i}. {news['title']}")
            print(f"   日期: {news['date']} | 内容: {content_len}字")
            print(f"   链接: {news['link']}")
        crawler.save_to_json(news_list)
    else:
        print("\n未获取到任何新闻")


if __name__ == '__main__':
    main()
