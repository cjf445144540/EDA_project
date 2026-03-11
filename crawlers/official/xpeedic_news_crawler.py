# -*- coding: utf-8 -*-
"""
芯和半导体官网新闻爬虫
来源：https://www.xpeedic.com/index.php?m=content&c=index&a=lists&catid=66
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import urllib3
import re
from datetime import datetime, timedelta

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XpedicNewsCrawler:
    """芯和半导体官网新闻爬虫"""

    BASE_URL = 'https://www.xpeedic.com'
    LIST_URL = 'https://www.xpeedic.com/index.php?m=content&c=index&a=lists&catid=66'

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.xpeedic.com/',
        }

    def crawl(self, max_pages=1, days=7):
        """
        爬取芯和半导体官网新闻
        :param max_pages: 最大爬取页数
        :param days: 只保留最近几天的新闻
        :return: 新闻列表
        """
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        print(f"\n正在爬取 芯和半导体官网 新闻（最近 {days} 天）...")

        for page in range(1, max_pages + 1):
            if page == 1:
                url = self.LIST_URL
            else:
                url = f'{self.LIST_URL}&page={page}'

            try:
                response = requests.get(url, headers=self.headers, timeout=20, verify=False)
                response.encoding = 'utf-8'

                if response.status_code != 200:
                    print(f"  第 {page} 页返回状态码: {response.status_code}")
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找新闻列表项 - 根据页面结构匹配
                # 新闻链接格式: index.php?m=content&c=index&a=show&catid=66&id=XXXX
                news_links = soup.find_all('a', href=re.compile(r'index\.php\?m=content&c=index&a=show&catid=66&id=\d+'))
                
                if not news_links:
                    print(f"  第 {page} 页未找到新闻")
                    break

                page_count = 0
                stop_crawl = False
                seen_urls = set()  # 避免重复
                
                for link in news_links:
                    href = link.get('href', '')
                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)
                    
                    # 获取标题
                    title = link.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # 构建完整URL
                    full_url = href if href.startswith('http') else f'{self.BASE_URL}/{href}'
                    
                    # 查找日期 - 通常在链接附近
                    parent = link.parent
                    date = ''
                    
                    # 查找日期文本（格式: YYYY-MM-DD）
                    if parent:
                        text = parent.get_text()
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                        if date_match:
                            date = date_match.group(1)
                    
                    # 如果没找到日期，尝试从更广范围查找
                    if not date:
                        grandparent = parent.parent if parent else None
                        if grandparent:
                            text = grandparent.get_text()
                            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                            if date_match:
                                date = date_match.group(1)
                    
                    # 检查日期是否在范围内
                    if date and date < cutoff_date:
                        stop_crawl = True
                        continue
                    
                    all_news.append({
                        'title': title,
                        'link': full_url,
                        'date': date,
                        'source': '芯和半导体官网',
                    })
                    page_count += 1

                print(f"  第 {page} 页: {page_count} 条新闻")

                if stop_crawl:
                    break

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

    def fetch_news_content(self, url):
        """获取新闻详情页的正文内容"""
        for attempt in range(3):
            try:
                response = requests.get(url, headers=self.headers, timeout=20, verify=False)
                response.encoding = 'utf-8'

                if response.status_code != 200:
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')

                # 芯和半导体详情页正文选择器（多个可能的位置）
                selectors = [
                    '.recruitDetailsConent .conent .jobText',
                    '.recruitDetailsConent .jobText',
                    '.recruitDetailsConent',
                    '.news-content',
                    '.content',
                    'article',
                    '.article-content'
                ]
                
                for selector in selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # 移除无关标签
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'figure', 'header', 'footer']):
                            tag.decompose()
                        
                        # 尝试从 <p> 标签获取
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                            if content and len(content) > 50:
                                return content
                        
                        # 没有 <p> 时直接取文本
                        text = content_elem.get_text(separator='\n', strip=True)
                        if text and len(text) > 50:
                            return text

                # 最后尝试从整个 body 提取
                body = soup.find('body')
                if body:
                    # 移除导航等无关内容
                    for tag in body.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        tag.decompose()
                    
                    # 查找所有段落
                    paragraphs = body.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                        if content and len(content) > 100:
                            return content

                return None

            except Exception:
                if attempt < 2:
                    import time
                    time.sleep(1)
                    continue
                return None

    def save_to_json(self, news_list, filename='xpeedic_news.json'):
        """保存新闻到 JSON 文件"""
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'json', 'official')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        data = {
            '芯和半导体': {
                '芯和半导体官网': [
                    {'title': n.get('title', ''), 'link': n.get('link', ''), 'date': n.get('date', '')}
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
    print("芯和半导体官网新闻爬虫")
    print("=" * 50)

    crawler = XpedicNewsCrawler()
    news_list = crawler.crawl(max_pages=3, days=7)

    if news_list:
        print("\n爬取结果预览：")
        for i, news in enumerate(news_list, 1):
            print(f"\n{i}. {news['title']}")
            print(f"   日期: {news['date']}")
            print(f"   链接: {news['link']}")
        crawler.save_to_json(news_list)
    else:
        print("\n未获取到任何新闻")


if __name__ == '__main__':
    main()
