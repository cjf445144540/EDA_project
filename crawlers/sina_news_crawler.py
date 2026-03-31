# -*- coding: utf-8 -*-
"""
新浪新闻搜索爬虫
通过关键词搜索爬取 https://search.sina.com.cn 的新闻
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import urllib3
from datetime import datetime, timedelta
import time

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SinaNewsCrawler:
    """新浪新闻搜索爬虫"""
    
    # 新浪搜索新接口
    SEARCH_API_URL = 'https://search.sina.com.cn/api/news'
    # 旧版页面地址（保留）
    SEARCH_URL = 'https://search.sina.com.cn/news'
    
    def __init__(self, keyword="EDA"):
        self.keyword = keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://search.sina.com.cn/',
            'Origin': 'https://search.sina.com.cn',
        }

    def _normalize_date(self, y, m, d):
        try:
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        except Exception:
            return ''

    def _parse_date_text(self, text):
        t = (text or '').strip()
        if not t:
            return ''
        now = datetime.now()
        m = re.search(r'(\d{4})[-/年\.](\d{1,2})[-/月\.](\d{1,2})', t)
        if m:
            return self._normalize_date(m.group(1), m.group(2), m.group(3))
        m = re.search(r'(\d{1,2})[-/月\.](\d{1,2})[日]?', t)
        if m:
            return self._normalize_date(now.year, m.group(1), m.group(2))
        if ('分钟前' in t) or ('小时前' in t) or ('分钟' in t and '前' in t) or ('小时' in t and '前' in t) or ('刚刚' in t) or ('今天' in t):
            return now.strftime('%Y-%m-%d')
        if '昨天' in t:
            return (now - timedelta(days=1)).strftime('%Y-%m-%d')
        m = re.search(r'(\d+)\s*天前', t)
        if m:
            return (now - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d')
        return ''

    def _extract_date_from_detail_html(self, html):
        if not html:
            return ''
        soup = BeautifulSoup(html, 'html.parser')
        candidates = []
        for sel in [
            'meta[property="article:published_time"]',
            'meta[property="og:release_date"]',
            'meta[name="publishdate"]',
            'meta[name="pubdate"]',
            'meta[itemprop="datePublished"]',
        ]:
            node = soup.select_one(sel)
            if node:
                candidates.append(node.get('content', ''))
        for sel in ['.date', '.time-source', '.article-time', '.pubtime', '#pub_date']:
            node = soup.select_one(sel)
            if node:
                candidates.append(node.get_text(' ', strip=True))
        script_text = soup.get_text('\n', strip=True)[:4000]
        candidates.append(script_text)
        for c in candidates:
            d = self._parse_date_text(c)
            if d:
                return d
        return ''
    
    def crawl(self, max_pages=3, days=7, min_content_length=500):
        """
        爬取新闻列表
        :param max_pages: 最大爬取页数
        :param days: 只保留最近几天的新闻
        :param min_content_length: 最小内容字数，低于此字数的新闻将被过滤
        :return: 新闻列表
        """
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 过滤关键词（标题包含这些词的将被跳过）
        skip_keywords = ['播', '直播', '视频直播', '在线直播', '预约']
        
        print(f"\n正在爬取 新浪网 新闻（关键词: {self.keyword}，最近 {days} 天）...")
        
        for page in range(1, max_pages + 1):
            try:
                response = requests.get(
                    self.SEARCH_API_URL,
                    params={
                        'q': self.keyword,
                        'page': page,
                        'size': 20,
                    },
                    headers=self.headers,
                    timeout=15,
                    verify=False,
                    proxies={'http': None, 'https': None}
                )
                if response.status_code != 200:
                    print(f"  第 {page} 页请求失败，状态码: {response.status_code}")
                    break

                payload = response.json()
                if payload.get('code') != 0:
                    print(f"  第 {page} 页接口返回异常: {payload.get('message', 'unknown')}")
                    break
                news_items = payload.get('data', {}).get('list', []) or []
                if not news_items:
                    print(f"  第 {page} 页没有找到新闻")
                    break
                
                page_count = 0
                
                for item in news_items:
                    title = item.get('title', '') or ''
                    link = item.get('url', '') or ''
                    
                    if not title or not link:
                        continue
                    
                    # 清理标题中的HTML标签（如高亮的<font>标签）
                    title = re.sub(r'<[^>]+>', '', title)
                    
                    date = ''
                    for key in ['dataTime', 'time', 'ctime', 'pubtime', 'pub_time', 'datetime']:
                        d = self._parse_date_text(item.get(key, ''))
                        if d:
                            date = d
                            break
                    
                    # 日期过滤
                    if date and date < cutoff_date:
                        continue
                    
                    # 标题关键词过滤（过滤直播相关）
                    if any(kw in title for kw in skip_keywords):
                        continue
                    
                    content, detail_date = self.fetch_news_content_and_date(link)
                    if not date and detail_date:
                        date = detail_date
                    content_len = len(content) if content else 0
                    
                    # 过滤500字以下的新闻
                    if content_len < min_content_length:
                        continue
                    
                    all_news.append({
                        'title': title,
                        'link': link,
                        'date': date,
                        'source': '新浪网',
                        'content': content,
                    })
                    page_count += 1
                
                print(f"  第 {page} 页: {page_count} 条新闻")
                
                # 礼貌等待
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  第 {page} 页出错: {e}")
                break
        
        # 去重（基于URL）
        unique_news = []
        seen = set()
        for news in all_news:
            if news['link'] not in seen:
                seen.add(news['link'])
                unique_news.append(news)
        
        print(f"  共获取 {len(unique_news)} 条新闻")
        return unique_news
    
    def fetch_news_content_and_date(self, url):
        """获取新闻详情页的正文内容和日期"""
        for attempt in range(3):
            try:
                response = requests.get(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    },
                    timeout=15,
                    verify=False,
                    proxies={'http': None, 'https': None}
                )
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    return None, ''
                
                soup = BeautifulSoup(response.text, 'html.parser')
                detail_date = self._extract_date_from_detail_html(response.text)
                
                # 新浪新闻详情页的正文选择器（多种可能）
                selectors = [
                    '#artibody',
                    '.article-content',
                    '.article',
                    '#article',
                    '.content',
                    'article',
                ]
                
                for selector in selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # 移除无关标签
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'figure', 'header', 'footer', 'iframe', '.article-editor']):
                            if hasattr(tag, 'decompose'):
                                tag.decompose()
                        
                        # 从 <p> 标签获取内容
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True) and len(p.get_text(strip=True)) > 10])
                            if content and len(content) > 100:
                                return content, detail_date
                        
                        # 直接获取文本
                        text = content_elem.get_text(separator='\n', strip=True)
                        if text and len(text) > 100:
                            return text, detail_date
                
                return None, detail_date
                
            except Exception:
                if attempt < 2:
                    time.sleep(1)
                    continue
                return None, ''

    def fetch_news_content(self, url):
        content, _ = self.fetch_news_content_and_date(url)
        return content
    
    def save_to_json(self, news_list, filename='sina_news.json'):
        """保存新闻到 JSON 文件"""
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        data = {
            '行业新闻': {
                '新浪网': [
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
    print("新浪新闻爬虫 (关键词: EDA)")
    print("=" * 50)
    
    crawler = SinaNewsCrawler(keyword="EDA")
    news_list = crawler.crawl(max_pages=3, days=7)
    
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
