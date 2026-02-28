# -*- coding: utf-8 -*-
"""
EETimes 新闻爬虫
从 EETimes 网站爬取 EDA 相关新闻
优先使用 RSS Feed（速度快、不受反爬影响）
https://www.eetimes.com/?s=EDA&feed=rss2
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import urllib3
import time
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EETimesNewsCrawler:
    """EETimes 新闻爬虫（基于 RSS Feed）"""

    def __init__(self):
        # RSS 请求使用轻量级 headers
        self.rss_headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RSS reader)',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        }
        # 详情页请求使用完整浏览器 headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def crawl(self, max_pages=1, days=7, keyword='EDA'):
        """
        通过 RSS Feed 爬取 EETimes 新闻（快速、稳定）
        :param max_pages: 最大爬取页数（RSS 暂不支持分页，保留参数兼容性）
        :param days: 只保留最近几天的新闻
        :param keyword: 搜索关键词
        :return: 新闻列表
        """
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        print(f"\n正在爬取 EETimes 新闻 (关键词: {keyword})...")

        # 主源: Google News RSS （过滤 eetimes.com）——国内访题快、稳定
        # 备用: EETimes 官方 RSS（可能因 Cloudflare 超时）
        rss_urls = [
            f"https://news.google.com/rss/search?q=site:eetimes.com+{keyword}&hl=en-US&gl=US&ceid=US:en",
            f"https://www.eetimes.com/?s={keyword}&feed=rss2",
            "https://www.eetimes.com/category/eda-design/feed/",
        ]

        seen_links = set()
        seen_lock = __import__('threading').Lock()

        def safe_fetch(url):
            return self._fetch_rss(url, cutoff_date, seen_links, seen_lock)

        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(safe_fetch, url): url for url in rss_urls}
            for future in as_completed(futures, timeout=30):
                try:
                    news_from_source = future.result()
                    all_news.extend(news_from_source)
                except Exception:
                    pass

        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        print(f"  获取 {len(all_news)} 条新闻")
        return all_news

    def _fetch_rss(self, rss_url, cutoff_date, seen_links, seen_lock):
        """从单个 RSS URL 获取新闻列表"""
        is_google_news = 'news.google.com' in rss_url
        news_list = []
        # 快速失败策略：连接超时 5s、读取超时 8s，只重试 1 次
        timeouts = [(5, 8), (5, 8)]
        for attempt, timeout in enumerate(timeouts):
            try:
                response = requests.get(rss_url, headers=self.rss_headers,
                                        timeout=timeout, verify=False)
                if response.status_code != 200:
                    return []

                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                if not items:
                    soup = BeautifulSoup(response.text, 'lxml')
                    items = soup.find_all('item')

                for item in items:
                    title_tag = item.find('title')
                    link_tag = item.find('link')
                    pub_date_tag = item.find('pubDate')

                    if not title_tag or not link_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    link = link_tag.get_text(strip=True) if link_tag.string else str(link_tag.next_sibling or '').strip()

                    # Google News RSS 需要过滤：只保留 eetimes.com 的条目
                    if is_google_news:
                        source_tag = item.find('source')
                        source_url = source_tag.get('url', '') if source_tag else ''
                        source_text = source_tag.get_text(strip=True) if source_tag else ''
                        if 'eetimes' not in source_url.lower() and 'eetimes' not in source_text.lower():
                            continue
                        guid_tag = item.find('guid')
                        if guid_tag:
                            guid = guid_tag.get_text(strip=True)
                            if guid.startswith('http') and 'eetimes' in guid:
                                link = guid

                    date = ''
                    if pub_date_tag:
                        date = self._parse_rss_date(pub_date_tag.get_text(strip=True))

                    if not link or link in seen_links:
                        continue
                    if date and date < cutoff_date:
                        continue

                    with seen_lock:
                        if link in seen_links:
                            continue
                        seen_links.add(link)
                    news_list.append({'title': title, 'link': link, 'date': date, 'source': 'EETimes'})

                return news_list

            except Exception:
                if attempt == 0:
                    time.sleep(1)
                    continue
                # 第二次也失败，静默放弃此源
                return []
        return []

    def _parse_rss_date(self, date_str):
        """解析 RSS 标准日期格式: 'Mon, 09 Feb 2026 12:00:00 +0000'"""
        try:
            dt = parsedate_to_datetime(date_str)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
        # 兜底：正则提取年月日
        try:
            months_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            match = re.search(r'(\d{1,2})\s+(\w{3})\s+(\d{4})', date_str)
            if match:
                day, month_str, year = match.groups()
                month = months_map.get(month_str, '01')
                return f"{year}-{month}-{day.zfill(2)}"
        except Exception:
            pass
        return ''

    def fetch_news_content(self, url):
        """获取新闻详情页的正文内容（带重试机制）"""
        for attempt in range(3):
            try:
                response = requests.get(url, headers=self.headers, timeout=20, verify=False)
                response.encoding = 'utf-8'

                if response.status_code != 200:
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')

                for selector in ['.article-content', '.entry-content', '.post-content', '.content-body', 'article .body', 'article']:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'figure', 'header', 'footer']):
                            tag.decompose()
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                            if content and len(content) > 50:
                                return content

                return None

            except Exception:
                if attempt < 2:
                    time.sleep(1)
                    continue
                return None

    def save_to_json(self, news_list, filename='eetimes_news.json'):
        """保存新闻到 JSON 文件"""
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        data = {"EETimes": {"EETimes": [{'title': n.get('title', ''), 'link': n.get('link', ''), 'date': n.get('date', '')} for n in news_list]}}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"新闻已保存到: {filepath}")
        return filepath


def main():
    print("=" * 50)
    print("EETimes 新闻爬虫")
    print("=" * 50)

    crawler = EETimesNewsCrawler()
    news_list = crawler.crawl(max_pages=1, days=7, keyword='EDA')

    if news_list:
        print("\n" + "=" * 50)
        print("爬取结果预览（前10条）：")
        print("=" * 50)
        for i, news in enumerate(news_list[:10], 1):
            print(f"\n{i}. {news['title'][:60]}{'...' if len(news['title']) > 60 else ''}")
            print(f"   日期: {news['date']}")
            print(f"   链接: {news['link']}")
        crawler.save_to_json(news_list)
    else:
        print("\n未获取到任何新闻")


if __name__ == '__main__':
    main()
