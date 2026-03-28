# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime, timedelta

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LaoyaobaNewsCrawler:
    SEARCH_API = "https://laoyaoba.com/api/search/index"

    def __init__(self, keyword="synopsys"):
        self.keyword = keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://laoyaoba.com/home/#/searchafter/article',
        }

    def _is_keyword_relevant(self, text):
        if not text:
            return False
        t = str(text).lower()
        keyword = (self.keyword or '').strip().lower()
        if keyword and keyword in t:
            return True
        if keyword == 'synopsys':
            return ('synopsys' in t) or ('新思科技' in str(text))
        return False

    def _to_date(self, ts):
        if ts is None:
            return ''
        try:
            ts = int(str(ts))
            if ts > 10**12:
                ts = ts // 1000
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        except Exception:
            return ''

    def _build_news_link(self, news_id, share_url):
        if news_id:
            return f"https://laoyaoba.com/n/{news_id}"
        if isinstance(share_url, str) and share_url.strip().startswith('http'):
            return share_url.strip()
        return "https://laoyaoba.com/home/#/searchafter/article"

    def _fetch_page(self, page_num=1, limit=20):
        data = {
            'query': self.keyword,
            'page': page_num,
            'limit': limit,
            'keyword_type': '自定义',
            'source': 'pc',
            'token': ''
        }
        resp = requests.post(
            self.SEARCH_API,
            data=data,
            headers=self.headers,
            timeout=20,
            verify=False
        )
        if resp.status_code != 200:
            return []
        payload = resp.json()
        if payload.get('errno') != 0:
            return []
        data_root = payload.get('data') or {}
        news_root = data_root.get('news') or {}
        return news_root.get('list') or []

    def crawl(self, max_pages=1, days=7, min_content_length=0):
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        all_news = []
        print(f"\n正在爬取 集微网（关键词: {self.keyword}，最近 {days} 天）...")
        for page_num in range(1, max_pages + 1):
            try:
                items = self._fetch_page(page_num=page_num, limit=20)
                if not items:
                    print(f"  第 {page_num} 页没有新闻")
                    break
                page_news = []
                for item in items:
                    title = (item.get('news_title') or '').strip()
                    if not title or not self._is_keyword_relevant(title):
                        continue
                    date = self._to_date(item.get('published_time'))
                    if not date or date < cutoff_date:
                        continue
                    link = self._build_news_link(item.get('news_id'), item.get('share_url'))
                    page_news.append({
                        'title': title,
                        'link': link,
                        'date': date,
                        'source': '集微网',
                    })
                if not page_news:
                    print(f"  第 {page_num} 页无符合条件新闻")
                    continue
                all_news.extend(page_news)
                print(f"  第 {page_num} 页: {len(page_news)} 条新闻")
            except Exception as e:
                print(f"  第 {page_num} 页出错: {e}")
                break

        unique_news = []
        seen_links = set()
        for n in all_news:
            link = n.get('link', '')
            if link and link not in seen_links:
                seen_links.add(link)
                unique_news.append(n)

        if min_content_length > 0 and unique_news:
            print(f"  正在获取新闻内容并过滤（>={min_content_length}字）...")
            filtered = []
            for n in unique_news:
                content = self.fetch_news_content(n['link'])
                if content and len(content) >= min_content_length:
                    n['content'] = content
                    filtered.append(n)
            unique_news = filtered

        print(f"  共获取 {len(unique_news)} 条新闻")
        return unique_news

    def fetch_news_content(self, url):
        try:
            resp = requests.get(
                url,
                headers={
                    'User-Agent': self.headers['User-Agent'],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': self.headers['Accept-Language'],
                    'Referer': 'https://laoyaoba.com/'
                },
                timeout=20,
                verify=False
            )
            if resp.status_code != 200:
                return ''
            resp.encoding = resp.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            node = soup.select_one('.article') or soup.select_one('.content')
            if not node:
                return ''
            for t in node(['script', 'style', 'noscript', 'iframe', 'form']):
                t.decompose()
            noisy_keys = ['related', 'recommend', 'hot', 'rank', 'sidebar', 'aside', 'topic', 'tag', 'share']
            for sub in list(node.find_all(True)):
                if not getattr(sub, 'attrs', None):
                    continue
                attrs = ' '.join([
                    sub.get('id') or '',
                    ' '.join(sub.get('class') or [])
                ]).lower()
                if attrs and any(k in attrs for k in noisy_keys):
                    sub.decompose()
            parts = []
            for elem in node.select('p, h1, h2, h3, h4'):
                cls = ' '.join(elem.get('class') or []).lower()
                if ('ell_two' in cls) or ('time' in cls):
                    continue
                txt = elem.get_text(' ', strip=True)
                txt = ' '.join(txt.split())
                if not txt or len(txt) < 8:
                    continue
                parts.append(txt)
            if not parts:
                text = node.get_text('\n', strip=True)
                parts = [' '.join(ln.split()) for ln in text.splitlines() if ln and len(ln.strip()) > 8]
            stop_markers = ['相关阅读', '相关推荐', '推荐阅读', '热门推荐', '延伸阅读', '最新文章', '相关链接', '微信扫一扫分享', '上市时间与更多资源', '微信：', '邮箱：']
            lines = []
            seen = set()
            for p in parts:
                if any(m in p for m in stop_markers):
                    break
                key = p.lower()
                if key in seen:
                    continue
                seen.add(key)
                lines.append(p)
            return '\n'.join(lines[:180])
        except Exception:
            return ''

    def save_to_json(self, news_list, filename='laoyaoba_news.json'):
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        data = {
            '行业新闻': {
                '集微网': [
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
    crawler = LaoyaobaNewsCrawler(keyword="synopsys")
    news_list = crawler.crawl(max_pages=2, days=30, min_content_length=0)
    crawler.save_to_json(news_list)


if __name__ == '__main__':
    main()
