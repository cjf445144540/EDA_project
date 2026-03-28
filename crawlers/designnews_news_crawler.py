# -*- coding: utf-8 -*-
import os
import json
import re
from urllib.parse import quote, urlparse, parse_qs, unquote
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DesignNewsCrawler:
    def __init__(self, keyword="EDA"):
        self.keyword = keyword
        self.rss_headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8',
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.designnews.com/',
        }

    def _build_keywords(self, keywords):
        if keywords:
            vals = [str(x).strip() for x in keywords if str(x).strip()]
            if vals:
                return vals
        key = (self.keyword or '').strip()
        if key:
            return [key]
        return ['EDA']

    def _is_keyword_relevant(self, text, keywords):
        t = (text or '').lower()
        for k in keywords:
            k2 = (k or '').strip().lower()
            if k2 and k2 in t:
                return True
        if 'synopsys' in [k.lower() for k in keywords]:
            return ('synopsys' in t) or ('新思' in text)
        if 'eda' in [k.lower() for k in keywords]:
            return ('eda' in t) or ('electronic design automation' in t)
        return False

    def _parse_rss_date(self, date_str):
        try:
            dt = parsedate_to_datetime(date_str)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
        m = re.search(r'(\d{1,2})\s+(\w{3})\s+(\d{4})', date_str or '')
        if not m:
            return ''
        day, mon, year = m.groups()
        mon_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        return f"{year}-{mon_map.get(mon, '01')}-{day.zfill(2)}"

    def _decode_bing_link(self, link):
        try:
            if 'bing.com/news/apiclick' not in (link or '').lower():
                return (link or '').strip()
            q = parse_qs(urlparse(link).query)
            target = q.get('url', [''])[0]
            target = unquote(target).strip()
            return target or (link or '').strip()
        except Exception:
            return (link or '').strip()

    def _is_news_like_link(self, link):
        u = (link or '').lower()
        if 'designnews.com' not in u:
            return False
        bad_parts = ['/author/', '/industry/', '/about', '/contact', '/tag/', '/topic/', '/events']
        if any(x in u for x in bad_parts):
            return False
        return True

    def _extract_from_html_search(self, html, cutoff_date):
        out = []
        seen = set()
        soup = BeautifulSoup(html or '', 'html.parser')
        for a in soup.find_all('a', href=True):
            raw = (a.get('href') or '').strip()
            if not raw:
                continue
            if raw.startswith('/news/apiclick'):
                raw = 'https://www.bing.com' + raw
            link = self._decode_bing_link(raw)
            if not self._is_news_like_link(link):
                continue
            title = ' '.join((a.get_text(' ', strip=True) or '').split())
            if len(title) < 8:
                continue
            key = f"{title}|{link}"
            if key in seen:
                continue
            seen.add(key)
            out.append({
                'title': title,
                'link': link,
                'date': '' if cutoff_date else '',
                'source': 'Design News',
            })
        return out

    def _fallback_seed_news(self):
        return [
            {
                'title': 'Data Analytics Becomes Staple of New EDA Tools',
                'link': 'https://www.designnews.com/design-software/data-analytics-becomes-staple-of-new-eda-tools',
                'date': '',
                'source': 'Design News',
            },
            {
                'title': 'EDA Analytics Tool Boosts SoC Design Productivity',
                'link': 'https://www.designnews.com/design-software/eda-analytics-tool-boosts-soc-design-productivity',
                'date': '',
                'source': 'Design News',
            },
            {
                'title': 'New Synopsys CEO Says Ansys Merger Gives Engineers Seamless Design Path',
                'link': 'https://www.designnews.com/electronics/new-synopsys-ceo-says-ansys-merger-gives-engineers-seamless-design-path',
                'date': '',
                'source': 'Design News',
            },
        ]

    def _fetch_rss(self, keyword, cutoff_date):
        queries = [
            f"site:designnews.com {keyword}",
            f"site:designnews.com {keyword} EDA",
            f"site:designnews.com {keyword} synopsys",
        ]
        urls = [
            f"https://www.bing.com/news/search?q={quote(q)}&format=rss&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR"
            for q in queries
        ]
        out = []
        seen = set()
        for url in urls:
            try:
                resp = requests.get(
                    url,
                    headers=self.rss_headers,
                    timeout=12,
                    verify=False,
                    allow_redirects=True
                )
                txt = (resp.text or '').strip()
                if not txt:
                    continue
                if ('<rss' in txt[:240].lower()) or ('<?xml' in txt[:240].lower()):
                    root = ET.fromstring(txt)
                    items = root.findall('./channel/item')
                    for item in items:
                        title = (item.findtext('title') or '').strip()
                        link = self._decode_bing_link((item.findtext('link') or '').strip())
                        if not title or not link:
                            continue
                        if not self._is_news_like_link(link):
                            continue
                        date = self._parse_rss_date((item.findtext('pubDate') or '').strip())
                        if cutoff_date and date and date < cutoff_date:
                            continue
                        key = f"{title}|{link}"
                        if key in seen:
                            continue
                        seen.add(key)
                        out.append({
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': 'Design News',
                        })
                else:
                    for n in self._extract_from_html_search(txt, cutoff_date):
                        key = f"{n.get('title', '')}|{n.get('link', '')}"
                        if key in seen:
                            continue
                        seen.add(key)
                        out.append(n)
            except Exception:
                continue
        return out

    def crawl(self, max_pages=1, days=7, min_content_length=0, keywords=None):
        kw_list = self._build_keywords(keywords)
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        print(f"\n正在爬取 Design News（关键词: {', '.join(kw_list)}，最近 {days} 天）...")
        all_news = []
        seen = set()
        for kw in kw_list:
            try:
                news = self._fetch_rss(kw, cutoff_date)
            except Exception:
                news = []
            page_count = 0
            for n in news:
                title = n.get('title', '')
                link = n.get('link', '')
                if not title or not link:
                    continue
                if not self._is_keyword_relevant(title, kw_list):
                    continue
                if link in seen:
                    continue
                seen.add(link)
                all_news.append(n)
                page_count += 1
            print(f"  关键词 {kw}: {page_count} 条新闻")

        if not all_news:
            print("  最近时间窗内未命中，回退为全量时间检索...")
            for kw in kw_list:
                try:
                    news = self._fetch_rss(kw, '')
                except Exception:
                    news = []
                page_count = 0
                for n in news:
                    title = n.get('title', '')
                    link = n.get('link', '')
                    if not title or not link:
                        continue
                    if not self._is_keyword_relevant(title, kw_list):
                        continue
                    if link in seen:
                        continue
                    seen.add(link)
                    all_news.append(n)
                    page_count += 1
                print(f"  关键词 {kw}（全量）: {page_count} 条新闻")

        if not all_news:
            print("  在线检索未命中，回退到站点已知新闻位置...")
            for n in self._fallback_seed_news():
                title = n.get('title', '')
                link = n.get('link', '')
                if not title or not link:
                    continue
                if not self._is_keyword_relevant(title, kw_list):
                    continue
                if link in seen:
                    continue
                seen.add(link)
                all_news.append(n)

        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        if min_content_length > 0 and all_news:
            print(f"  正在获取新闻内容并过滤（>={min_content_length}字）...")
            filtered = []
            for n in all_news:
                content = self.fetch_news_content(n.get('link', ''))
                if content and len(content) >= min_content_length:
                    n['content'] = content
                    filtered.append(n)
            all_news = filtered
        print(f"  共获取 {len(all_news)} 条新闻")
        return all_news

    def fetch_news_content(self, url):
        if not url:
            return ''
        try:
            resp = requests.get(url, headers=self.headers, timeout=20, verify=False, allow_redirects=True)
            if resp.status_code != 200:
                return ''
            resp.encoding = resp.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            selectors = ['article', '.article-content', '.entry-content', '.post-content', '.content-body', '.field--name-body']
            for sel in selectors:
                node = soup.select_one(sel)
                if not node:
                    continue
                for t in node(['script', 'style', 'noscript', 'iframe', 'form', 'nav', 'aside']):
                    t.decompose()
                lines = []
                for p in node.find_all('p'):
                    txt = ' '.join((p.get_text(' ', strip=True) or '').split())
                    if txt and len(txt) > 20:
                        lines.append(txt)
                if lines:
                    return '\n'.join(lines[:200])
                txt = node.get_text('\n', strip=True)
                parts = [x.strip() for x in txt.splitlines() if x.strip() and len(x.strip()) > 20]
                if parts:
                    return '\n'.join(parts[:200])
            return ''
        except Exception:
            return ''

    def save_to_json(self, news_list, filename='designnews_news.json'):
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        data = {
            '行业新闻': {
                'Design News': [
                    {
                        'title': n.get('title', ''),
                        'link': n.get('link', ''),
                        'date': n.get('date', ''),
                        'content': n.get('content', '')
                    }
                    for n in news_list
                ]
            }
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"新闻已保存到: {filepath}")
        return filepath


def main():
    crawler = DesignNewsCrawler(keyword='EDA')
    news = crawler.crawl(days=7, keywords=['EDA', 'synopsys'])
    crawler.save_to_json(news)


if __name__ == '__main__':
    main()
