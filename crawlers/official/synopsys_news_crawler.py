# -*- coding: utf-8 -*-
"""
Synopsys 新闻爬虫
从多个来源爬取 Synopsys 相关新闻：
- SemiWiki
- Design-Reuse
- Synopsys 官网
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


class SynopsysNewsCrawler:
    """Synopsys 新闻爬虫"""
    
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
        # days 优先，months 作为兼容
        if months is not None and days == 7:
            actual_days = months * 30
        else:
            actual_days = days
        
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=actual_days)).strftime('%Y-%m-%d')
        
        # 1. 爬取 SemiWiki
        print("\n[1/3] 正在爬取 SemiWiki...")
        semiwiki_news = self._crawl_semiwiki(max_pages, cutoff_date)
        all_news.extend(semiwiki_news)
        print(f"  获取 {len(semiwiki_news)} 条新闻")
        
        # 2. 爬取 Design-Reuse
        print("\n[2/3] 正在爬取 Design-Reuse...")
        designreuse_news = self._crawl_designreuse(max_pages, cutoff_date)
        all_news.extend(designreuse_news)
        print(f"  获取 {len(designreuse_news)} 条新闻")
        
        # 3. 爬取 Synopsys 官网
        print("\n[3/3] 正在爬取 Synopsys 官网...")
        synopsys_news = self._crawl_synopsys_official(max_pages, cutoff_date)
        all_news.extend(synopsys_news)
        print(f"  获取 {len(synopsys_news)} 条新闻")
        
        # 按日期排序（最新的在前）
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
        base_url = "https://semiwiki.com/category/eda/synopsys/"
        
        for page in range(1, max_pages + 1):
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}page/{page}/"
            
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
                    # 获取标题和链接
                    title_elem = article.select_one('h2 a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 获取日期
                    article_text = article.get_text()
                    date = self._parse_semiwiki_date(article_text)
                    
                    if date and date >= cutoff_date:
                        news_list.append({
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': 'SemiWiki'
                        })
                    elif date and date < cutoff_date:
                        # 遇到旧新闻，停止爬取
                        return news_list
                        
            except Exception as e:
                print(f"  爬取 SemiWiki 第 {page} 页出错: {e}")
                break
        
        return news_list
    
    def _parse_designreuse_date(self, date_str):
        """解析 Design-Reuse 日期格式: '(Tuesday, February 24, 2026)'"""
        try:
            # 移除括号
            date_str = date_str.strip('()')
            # 解析: "Tuesday, February 24, 2026"
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
            if page == 0:
                url = f"{base_url}?search_in=synopsys"
            else:
                url = f"{base_url}?p={page}&search_in=synopsys"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=15, verify=False)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找所有新闻链接
                news_links = soup.select('a[href*="/news/202"]')
                
                if not news_links:
                    break
                
                for link_elem in news_links:
                    href = link_elem.get('href', '')
                    if not href or '/news/202' not in href:
                        continue
                    
                    # 获取标题
                    title_span = link_elem.select_one('span')
                    if not title_span:
                        continue
                    title = title_span.get_text(strip=True)
                    
                    # 获取日期
                    date_elem = link_elem.select_one('i')
                    date = ''
                    if date_elem:
                        date = self._parse_designreuse_date(date_elem.get_text())
                    
                    # 构建完整链接
                    if href.startswith('/'):
                        full_url = f"https://www.design-reuse.com{href}"
                    else:
                        full_url = href
                    
                    # 避免重复
                    if any(n['link'] == full_url for n in news_list):
                        continue
                    
                    if date and date >= cutoff_date:
                        news_list.append({
                            'title': title,
                            'link': full_url,
                            'date': date,
                            'source': 'Design-Reuse'
                        })
                    elif date and date < cutoff_date:
                        return news_list
                        
            except Exception as e:
                print(f"  爬取 Design-Reuse 第 {page+1} 页出错: {e}")
                break
        
        return news_list
    
    def _parse_synopsys_date(self, date_str):
        """解析 Synopsys 官网日期格式: 'FEB 19, 2026'"""
        try:
            months = {
                'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
            }
            match = re.search(r'(\w{3})\s+(\d+),?\s+(\d{4})', date_str.upper())
            if match:
                month_str, day, year = match.groups()
                month = months.get(month_str, '01')
                return f"{year}-{month}-{day.zfill(2)}"
        except:
            pass
        return ''
    
    def _crawl_synopsys_official(self, max_pages, cutoff_date):
        """爬取 Synopsys 官网新闻"""
        news_list = []
        base_url = "https://news.synopsys.com/"
        
        for page in range(max_pages):
            if page == 0:
                url = base_url
            else:
                url = f"{base_url}?o={page * 5}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=15, verify=False)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找新闻项
                # 新闻链接格式: /2026-02-19-xxx
                news_links = soup.select('a[href*="/202"]')
                
                seen_links = set()
                for link_elem in news_links:
                    href = link_elem.get('href', '')
                    
                    # 只处理新闻链接格式
                    if not re.match(r'^/\d{4}-\d{2}-\d{2}', href):
                        continue
                    
                    # 避免重复（缩略图和标题可能是同一链接）
                    if href in seen_links:
                        continue
                    seen_links.add(href)
                    
                    title = link_elem.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    # 从链接提取日期
                    date_match = re.match(r'^/(\d{4})-(\d{2})-(\d{2})', href)
                    date = ''
                    if date_match:
                        year, month, day = date_match.groups()
                        date = f"{year}-{month}-{day}"
                    
                    full_url = f"https://news.synopsys.com{href}"
                    
                    if date and date >= cutoff_date:
                        news_list.append({
                            'title': title,
                            'link': full_url,
                            'date': date,
                            'source': 'Synopsys官网'
                        })
                    elif date and date < cutoff_date:
                        return news_list
                        
            except Exception as e:
                print(f"  爬取 Synopsys 官网第 {page+1} 页出错: {e}")
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
                        # 提取 read more 原始链接（用于后续追取）
                        read_more_link = None
                        for a in content_elem.find_all('a'):
                            if 'read more' in a.get_text(strip=True).lower() or 'click here' in a.get_text(strip=True).lower():
                                read_more_link = a.get('href', '')
                                break
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            # 过滤掉 click here to read more 段落
                            content_parts = []
                            for p in paragraphs:
                                txt = p.get_text(strip=True)
                                if txt and 'click here' not in txt.lower() and 'read more' not in txt.lower():
                                    content_parts.append(txt)
                            content = '\n'.join(content_parts)
                            # 尝试追进原始链接获取更多内容
                            if read_more_link and read_more_link.startswith('http'):
                                try:
                                    orig_resp = requests.get(read_more_link, headers=self.headers, timeout=15, verify=False)
                                    if orig_resp.status_code == 200:
                                        orig_soup = BeautifulSoup(orig_resp.text, 'html.parser')
                                        orig_text = None
                                        # 常规选择器
                                        for sel in ['.press-release-content', '.article-content', '.entry-content', '.post-content', '.content-body', 'article main', 'article']:
                                            orig_elem = orig_soup.select_one(sel)
                                            if orig_elem:
                                                for tag in orig_elem.find_all(['script', 'style', 'nav', 'aside', 'figure']):
                                                    tag.decompose()
                                                orig_paras = orig_elem.find_all('p')
                                                orig_text = '\n'.join([p.get_text(strip=True) for p in orig_paras if p.get_text(strip=True)])
                                                if orig_text and len(orig_text) > 100:
                                                    break
                                                orig_text = None
                                        # 内容不足时尝试全页 <p> 小段落拼接（兼容 Elementor 等 Page Builder）
                                        if not orig_text or len(orig_text) <= 100:
                                            all_paras = orig_soup.find_all('p')
                                            long_paras = [p.get_text(strip=True) for p in all_paras
                                                         if len(p.get_text(strip=True)) > 80
                                                         and 'read more' not in p.get_text(strip=True).lower()
                                                         and 'click here' not in p.get_text(strip=True).lower()]
                                            if long_paras:
                                                orig_text = '\n'.join(long_paras)
                                        if orig_text and len(orig_text) > len(content):
                                            return orig_text
                                except Exception:
                                    pass
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
    
    def save_to_json(self, news_list, filename='synopsys_news.json'):
        """保存新闻到 JSON 文件"""
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'json', 'official')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 按来源分组
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
        
        # 三级嵌套格式
        data = {
            "Synopsys": by_source
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"新闻已保存到: {filepath}")
        return filepath


def main():
    """主函数"""
    print("=" * 50)
    print("Synopsys 新闻爬虫")
    print("=" * 50)
    
    crawler = SynopsysNewsCrawler()
    
    # 爬取新闻（默认1页，最近1个月）
    news_list = crawler.crawl(max_pages=1, months=1)
    
    if news_list:
        print("\n" + "=" * 50)
        print(f"爬取结果预览（前10条）：")
        print("=" * 50)
        
        for i, news in enumerate(news_list[:10], 1):
            print(f"\n{i}. [{news['source']}] {news['title'][:50]}{'...' if len(news['title']) > 50 else ''}")
            print(f"   日期: {news['date']}")
            print(f"   链接: {news['link']}")
        
        # 保存到 JSON
        crawler.save_to_json(news_list)
    else:
        print("\n未获取到任何新闻")


if __name__ == '__main__':
    main()
