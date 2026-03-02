# -*- coding: utf-8 -*-
"""
思尔芯 (S2C EDA) 官网新闻爬虫
来源：https://www.s2ceda.com/ch/info-pr
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import urllib3
from datetime import datetime, timedelta

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class S2CNewsCrawler:
    """思尔芯官网新闻爬虫"""

    BASE_URL = 'https://www.s2ceda.com'

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.s2ceda.com/ch/info-pr',
        }

    def crawl(self, max_pages=1, days=7):
        """
        爬取思尔芯官网新闻
        :param max_pages: 最大爬取页数
        :param days: 只保留最近几天的新闻
        :return: 新闻列表
        """
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        print(f"\n正在爬取 思尔芯官网 新闻（最近 {days} 天）...")

        for page in range(1, max_pages + 1):
            if page == 1:
                url = f'{self.BASE_URL}/ch/info-pr'
            else:
                url = f'{self.BASE_URL}/ch/info-pr_{page}'

            try:
                response = requests.get(url, headers=self.headers, timeout=20, verify=False)
                response.encoding = 'utf-8'

                if response.status_code != 200:
                    print(f"  第 {page} 页返回状态码: {response.status_code}")
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.select('.t_f2li')

                if not items:
                    break

                page_count = 0
                stop_crawl = False
                for item in items:
                    title_elem = item.select_one('.t_f2tit')
                    link_elem = item.select_one('a[href*="/ch/info-pr-"]')
                    date_elem = item.select_one('.t_f2time')

                    if not title_elem or not link_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    href = link_elem.get('href', '')
                    link = href if href.startswith('http') else f'{self.BASE_URL}{href}'
                    date = date_elem.get_text(strip=True) if date_elem else ''

                    if date and date < cutoff_date:
                        stop_crawl = True
                        break

                    if title and link:
                        all_news.append({
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': '思尔芯官网',
                        })
                        page_count += 1

                print(f"  第 {page} 页: {page_count} 条新闻")

                if stop_crawl:
                    break

            except Exception as e:
                print(f"  第 {page} 页出错: {e}")
                break

        print(f"  共获取 {len(all_news)} 条新闻")
        return all_news

    def fetch_news_content(self, url):
        """获取新闻详情页的正文内容"""
        for attempt in range(3):
            try:
                response = requests.get(url, headers=self.headers, timeout=20, verify=False)
                response.encoding = 'utf-8'

                if response.status_code != 200:
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')

                # 思尔芯详情页正文选择器
                for selector in ['.t_f3k2wen', '.t_content2 .t_f3k2wen', '.t_content2', '.news-content', 'article']:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'figure']):
                            tag.decompose()
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                            if content and len(content) > 50:
                                return content
                        # 没有 <p> 时直接取文本
                        text = content_elem.get_text(separator='\n', strip=True)
                        if text and len(text) > 50:
                            return text

                return None

            except Exception:
                if attempt < 2:
                    import time
                    time.sleep(1)
                    continue
                return None

    def save_to_json(self, news_list, filename='s2c_news.json'):
        """保存新闻到 JSON 文件"""
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        data = {
            '思尔芯': {
                '思尔芯官网': [
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
    print("思尔芯官网新闻爬虫")
    print("=" * 50)

    crawler = S2CNewsCrawler()
    news_list = crawler.crawl(max_pages=3, days=30)

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
