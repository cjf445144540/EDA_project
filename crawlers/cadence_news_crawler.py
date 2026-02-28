# -*- coding: utf-8 -*-
"""
Cadence 新闻爬虫
从多个来源爬取 Cadence 相关新闻：
- SemiWiki
- Design-Reuse
- Cadence 官网
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import urllib3
from datetime import datetime, timedelta

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CadenceNewsCrawler:
    """Cadence 新闻爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        }

    def crawl(self, max_pages=1, days=7, months=None):
        """
        从所有来源爬取新闻
        :param max_pages: 每个来源最大爬取页数
        :param days: 只保留最近几天的新闻（优先）
        :param months: 只保留最近几个月的新闻（兼容旧参数）
        :return: 新闻列表
        """
        if months is not None and days == 7:
            actual_days = months * 30
        else:
            actual_days = days

        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=actual_days)).strftime('%Y-%m-%d')

        print("\n[1/2] 正在爬取 SemiWiki...")
        semiwiki_news = self._crawl_semiwiki(max_pages, cutoff_date)
        all_news.extend(semiwiki_news)
        print(f"  获取 {len(semiwiki_news)} 条新闻")

        print("\n[2/2] 正在爬取 Design-Reuse...")
        designreuse_news = self._crawl_designreuse(max_pages, cutoff_date)
        all_news.extend(designreuse_news)
        print(f"  获取 {len(designreuse_news)} 条新闻")

        # Cadence 官网有反爬保护（403），暂时跳过

        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        print(f"\n总共获取 {len(all_news)} 条新闻（最近{actual_days}天）")
        return all_news

    def _parse_semiwiki_date(self, date_str):
        """解析 SemiWiki 日期格式: 'on 02-23-2026 at 10:00 am'"""
        try:
            match = re.search(r'(\d{2})-(\d{2})-(\d{4})', date_str)
            if match:
                month, day, year = match.groups()
                return f"{year}-{month}-{day}"
        except:
            pass
        return ''

    def _crawl_semiwiki(self, max_pages, cutoff_date):
        """爬取 SemiWiki 新闻"""
        news_list = []
        base_url = "https://semiwiki.com/category/eda/cadence/"

        for page in range(1, max_pages + 1):
            url = base_url if page == 1 else f"{base_url}page/{page}/"
            try:
                response = requests.get(url, headers=self.headers, timeout=15, verify=False)
                response.encoding = 'utf-8'
                if response.status_code != 200:
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.select('article.post')
                if not articles:
                    break

                for article in articles:
                    title_elem = article.select_one('h2 a')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    date = self._parse_semiwiki_date(article.get_text())

                    if date and date >= cutoff_date:
                        news_list.append({'title': title, 'link': link, 'date': date, 'source': 'SemiWiki'})
                    elif date and date < cutoff_date:
                        return news_list

            except Exception as e:
                print(f"  爬取 SemiWiki 第 {page} 页出错: {e}")
                break

        return news_list

    def _parse_designreuse_date(self, date_str):
        """解析 Design-Reuse 日期格式: '(Tuesday, February 24, 2026)'"""
        try:
            date_str = date_str.strip('()')
            match = re.search(r'(\w+)\s+(\d+),?\s+(\d{4})', date_str)
            if match:
                month_str, day, year = match.groups()
                months = {
                    'January': '01', 'February': '02', 'March': '03', 'April': '04',
                    'May': '05', 'June': '06', 'July': '07', 'August': '08',
                    'September': '09', 'October': '10', 'November': '11', 'December': '12'
                }
                month = months.get(month_str, '01')
                return f"{year}-{month}-{day.zfill(2)}"
        except:
            pass
        return ''

    def _crawl_designreuse(self, max_pages, cutoff_date):
        """爬取 Design-Reuse 新闻"""
        news_list = []
        base_url = "https://www.design-reuse.com/news/list/"

        for page in range(max_pages):
            url = f"{base_url}?search_in=cadence" if page == 0 else f"{base_url}?p={page}&search_in=cadence"
            try:
                response = requests.get(url, headers=self.headers, timeout=15, verify=False)
                response.encoding = 'utf-8'
                if response.status_code != 200:
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                news_links = soup.select('a[href*="/news/202"]')
                if not news_links:
                    break

                for link_elem in news_links:
                    href = link_elem.get('href', '')
                    if not href or '/news/202' not in href:
                        continue

                    title_span = link_elem.select_one('span')
                    if not title_span:
                        continue
                    title = title_span.get_text(strip=True)

                    date_elem = link_elem.select_one('i')
                    date = self._parse_designreuse_date(date_elem.get_text()) if date_elem else ''

                    full_url = f"https://www.design-reuse.com{href}" if href.startswith('/') else href

                    if any(n['link'] == full_url for n in news_list):
                        continue

                    if date and date >= cutoff_date:
                        news_list.append({'title': title, 'link': full_url, 'date': date, 'source': 'Design-Reuse'})
                    elif date and date < cutoff_date:
                        return news_list

            except Exception as e:
                print(f"  爬取 Design-Reuse 第 {page+1} 页出错: {e}")
                break

        return news_list

    def _parse_cadence_date(self, date_str):
        """解析 Cadence 官网日期格式: '23 Feb 2026'"""
        try:
            months = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            match = re.search(r'(\d{1,2})\s+(\w{3})\s+(\d{4})', date_str)
            if match:
                day, month_str, year = match.groups()
                month = months.get(month_str, '01')
                return f"{year}-{month}-{day.zfill(2)}"
        except:
            pass
        return ''

    def _crawl_cadence_official(self, max_pages, cutoff_date):
        """爬取 Cadence 官网新闻"""
        news_list = []
        rows_per_page = 10
        base_url = (
            "https://www.cadence.com/en_US/home/company/newsroom/press-releases.html"
            "?refinementfilters=AEMTemplate:%2Fapps%2Fcadence-www%2Ftemplates%2Fpage_newsroom_detail"
            "&sortList=AEMPublished:descending"
            f"&rowsPerPage={rows_per_page}"
        )

        for page in range(max_pages):
            start = page * rows_per_page
            url = f"{base_url}&start={start}"
            try:
                response = requests.get(url, headers=self.headers, timeout=15, verify=False)
                response.encoding = 'utf-8'
                if response.status_code != 200:
                    break

                soup = BeautifulSoup(response.text, 'html.parser')

                # 容器：li.search-result-entry
                items = soup.select('li.search-result-entry')
                if not items:
                    break

                for item in items:
                    # 标题和链接
                    title_elem = item.select_one('.eantry-container h5 a')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    if href.startswith('/'):
                        full_url = f"https://www.cadence.com{href}"
                    else:
                        full_url = href

                    # 日期：从 .type 的文本节点提取（格式: 23 Feb 2026）
                    type_elem = item.select_one('.eantry-container .type')
                    date = ''
                    if type_elem:
                        date = self._parse_cadence_date(type_elem.get_text())

                    if date and date >= cutoff_date:
                        news_list.append({'title': title, 'link': full_url, 'date': date, 'source': 'Cadence官网'})
                    elif date and date < cutoff_date:
                        return news_list

            except Exception as e:
                print(f"  爬取 Cadence 官网第 {page+1} 页出错: {e}")
                break

        return news_list

    def fetch_news_content(self, url):
        """获取新闻详情页的正文内容（带重试机制）"""
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=20, verify=False)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Design-Reuse 专用选择器
                if 'design-reuse.com' in url:
                    news_contents = soup.select('.news_content')
                    if len(news_contents) >= 3:
                        content_elem = news_contents[2]
                        read_more_link = None
                        for a in content_elem.find_all('a'):
                            if 'read more' in a.get_text(strip=True).lower() or 'click here' in a.get_text(strip=True).lower():
                                read_more_link = a.get('href', '')
                                break
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content_parts = []
                            for p in paragraphs:
                                txt = p.get_text(strip=True)
                                if txt and 'click here' not in txt.lower() and 'read more' not in txt.lower():
                                    content_parts.append(txt)
                            content = '\n'.join(content_parts)
                            if read_more_link and read_more_link.startswith('http'):
                                try:
                                    orig_resp = requests.get(read_more_link, headers=self.headers, timeout=15, verify=False)
                                    if orig_resp.status_code == 200:
                                        orig_soup = BeautifulSoup(orig_resp.text, 'html.parser')
                                        for sel in ['.press-release-content', '.article-content', '.entry-content', '.post-content', '.content-body', 'article main', 'article']:
                                            orig_elem = orig_soup.select_one(sel)
                                            if orig_elem:
                                                for tag in orig_elem.find_all(['script', 'style', 'nav', 'aside', 'figure']):
                                                    tag.decompose()
                                                orig_paras = orig_elem.find_all('p')
                                                orig_text = '\n'.join([p.get_text(strip=True) for p in orig_paras if p.get_text(strip=True)])
                                                if orig_text and len(orig_text) > len(content):
                                                    return orig_text
                                                break
                                except Exception:
                                    pass
                            if content and len(content) > 50:
                                return content
                
                # Cadence 官网专用选择器
                if 'cadence.com' in url:
                    for selector in ['.press-release-content', '.newsroom-content', '.article-body', '.cds-body']:
                        content_elem = soup.select_one(selector)
                        if content_elem:
                            paragraphs = content_elem.find_all('p')
                            if paragraphs:
                                content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                                if content and len(content) > 50:
                                    return content
                
                # 通用选择器
                for selector in ['.entry-content', '.article-content', '.news-content', '.post-content', 'article', '.content']:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'aside']):
                            tag.decompose()
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                            if content and len(content) > 50:
                                return content
                
                return None
                
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None
    
    def save_to_json(self, news_list, filename='cadence_news.json'):
        """保存新闻到 JSON 文件"""
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        by_source = {}
        for news in news_list:
            source = news.get('source', '未知来源')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append({
                'title': news.get('title', ''),
                'link': news.get('link', ''),
                'date': news.get('date', '')
            })

        data = {"Cadence": by_source}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"新闻已保存到: {filepath}")
        return filepath


def main():
    print("=" * 50)
    print("Cadence 新闻爬虫")
    print("=" * 50)

    crawler = CadenceNewsCrawler()
    news_list = crawler.crawl(max_pages=1, days=7)

    if news_list:
        print("\n" + "=" * 50)
        print(f"爬取结果预览（前10条）：")
        print("=" * 50)
        for i, news in enumerate(news_list[:10], 1):
            print(f"\n{i}. [{news['source']}] {news['title'][:50]}{'...' if len(news['title']) > 50 else ''}")
            print(f"   日期: {news['date']}")
            print(f"   链接: {news['link']}")
        crawler.save_to_json(news_list)
    else:
        print("\n未获取到任何新闻")


if __name__ == '__main__':
    main()
