# -*- coding: utf-8 -*-
"""
鸿芯微纳官网新闻爬虫
来源：https://www.giga-da.com/article.html
- 列表第一页：HTML 直接解析
- 后续分页：POST API /ajaxarticle
- 链接类型：内部文章 /detail/{id}.html 或微信公众号文章
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import urllib3
from datetime import datetime, timedelta

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GigaDANewsCrawler:
    """鸿芯微纳官网新闻爬虫"""

    BASE_URL = 'https://www.giga-da.com'
    LIST_URL = 'https://www.giga-da.com/article.html'
    API_URL = 'https://www.giga-da.com/ajaxarticle'

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.giga-da.com/article.html',
        }
        self.api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.giga-da.com/article.html',
            'Origin': 'https://www.giga-da.com',
        }

    def crawl(self, max_pages=5, days=7):
        """
        爬取鸿芯微纳官网新闻
        :param max_pages: 最大爬取页数
        :param days: 只保留最近几天的新闻
        :return: 新闻列表
        """
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        print(f"\n正在爬取 鸿芯微纳官网 新闻（最近 {days} 天）...")

        # ---- 第一页：从 HTML 解析 ----
        try:
            resp = requests.get(self.LIST_URL, headers=self.headers, timeout=20, verify=False)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select('ul#news li')
                page_count = 0
                stop_crawl = False
                for li in items:
                    a = li.select_one('a')
                    if not a:
                        continue
                    href = a.get('href', '')
                    link = href if href.startswith('http') else f'{self.BASE_URL}{href}'
                    h3 = a.select_one('h3')
                    title = h3.get_text(strip=True) if h3 else ''
                    # 日期在 <div> 内第一个 <p>
                    div = a.select_one('div')
                    p_tags = div.find_all('p') if div else []
                    date = p_tags[0].get_text(strip=True) if p_tags else ''

                    if not title or not link:
                        continue
                    if date and date < cutoff_date:
                        stop_crawl = True
                        break
                    all_news.append({'title': title, 'link': link, 'date': date, 'source': '鸿芯微纳官网'})
                    page_count += 1

                print(f"  第 1 页（HTML）: {page_count} 条新闻")
                if stop_crawl:
                    print(f"  共获取 {len(all_news)} 条新闻")
                    return all_news
        except Exception as e:
            print(f"  第 1 页（HTML）出错: {e}")

        # ---- 后续页：POST API ----
        for page in range(2, max_pages + 1):
            try:
                data = f'page={page}&cate_id=0'
                resp = requests.post(self.API_URL, headers=self.api_headers,
                                     data=data, timeout=20, verify=False)
                if resp.status_code != 200:
                    break

                result = resp.json()
                items = result.get('data', [])
                if not items:
                    break

                page_count = 0
                stop_crawl = False
                for item in items:
                    title = item.get('title', '').strip()
                    date = (item.get('create_time') or '').strip()[:10]  # 取 YYYY-MM-DD 部分
                    # 构造链接
                    if item.get('type') == 1:
                        link = f"{self.BASE_URL}/detail/{item['id']}.html"
                    else:
                        link = item.get('linkurl', '')

                    if not title or not link:
                        continue
                    if date and date < cutoff_date:
                        stop_crawl = True
                        break
                    all_news.append({'title': title, 'link': link, 'date': date, 'source': '鸿芯微纳官网'})
                    page_count += 1

                print(f"  第 {page} 页（API）: {page_count} 条新闻")
                if stop_crawl:
                    break

                time.sleep(0.5)

            except Exception as e:
                print(f"  第 {page} 页（API）出错: {e}")
                break

        print(f"  共获取 {len(all_news)} 条新闻")
        return all_news

    def fetch_news_content(self, url):
        """获取新闻详情页的正文内容（支持内部页面和微信公众号文章）"""
        for attempt in range(3):
            try:
                response = requests.get(url, headers=self.headers, timeout=20, verify=False)
                response.encoding = 'utf-8'

                if response.status_code != 200:
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')

                # 微信公众号文章
                if 'mp.weixin.qq.com' in url:
                    content_elem = soup.select_one('#js_content')
                    if content_elem:
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'aside']):
                            tag.decompose()
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                            if content and len(content) > 50:
                                return content
                        text = content_elem.get_text(separator='\n', strip=True)
                        if text and len(text) > 50:
                            return text

                # 内部文章 /detail/
                for selector in ['.content', '.news_content', '.article-content', '.detail-content', 'article']:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'figure']):
                            tag.decompose()
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                            if content and len(content) > 50:
                                return content
                        text = content_elem.get_text(separator='\n', strip=True)
                        if text and len(text) > 50:
                            return text

                return None

            except Exception:
                if attempt < 2:
                    time.sleep(1)
                    continue
                return None

    def save_to_json(self, news_list, filename='gigada_news.json'):
        """保存新闻到 JSON 文件"""
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'json', 'official')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        data = {
            '鸿芯微纳': {
                '鸿芯微纳官网': [
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
    print("鸿芯微纳官网新闻爬虫")
    print("=" * 50)

    crawler = GigaDANewsCrawler()
    news_list = crawler.crawl(max_pages=5, days=30)

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
