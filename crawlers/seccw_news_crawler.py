# -*- coding: utf-8 -*-
"""
深圳电子商会新闻爬虫
通过关键词搜索爬取 https://www.seccw.com 的新闻
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


class SeccwNewsCrawler:
    """深圳电子商会新闻爬虫"""
    
    def __init__(self, keyword="EDA"):
        self.base_url = "https://www.seccw.com"
        self.keyword = keyword
        # 分页URL格式
        self.search_url_template = "https://www.seccw.com/Index/search/k/{keyword}/p/{page}.html"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def crawl(self, max_pages=1, days=7):
        """
        爬取新闻列表
        :param max_pages: 最大爬取页数，默认1页
        :param days: 只保留最近几天的新闻，默认7天
        :return: 新闻列表
        """
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        stop_crawling = False
        
        for page in range(1, max_pages + 1):
            if stop_crawling:
                break
                
            print(f"正在爬取第 {page} 页...")
            
            # 构建分页 URL
            url = self.search_url_template.format(keyword=self.keyword, page=page)
            
            news_list = self._crawl_page(url)
            
            if not news_list:
                print(f"第 {page} 页没有获取到新闻，停止爬取")
                break
            
            # 获取每条新闻的日期（从详情页）
            filtered_news = []
            has_old_news = False
            
            for news in news_list:
                # 获取详情页的日期
                detail_info = self._get_news_detail(news['link'])
                if detail_info:
                    news['date'] = detail_info.get('date', '')
                    news['content'] = detail_info.get('content', '')
                
                news_date = news.get('date', '')
                if news_date and news_date >= cutoff_date:
                    filtered_news.append(news)
                elif news_date and news_date < cutoff_date:
                    has_old_news = True
            
            # 如果大部分新闻都是旧的，停止爬取
            if has_old_news and len(filtered_news) < len(news_list) // 2:
                stop_crawling = True
                print(f"  遇到大量超过{months}个月的新闻，停止爬取")
            
            all_news.extend(filtered_news)
            print(f"第 {page} 页获取 {len(filtered_news)} 条新闻（最近{months}个月）")
        
        # 按日期排序（最新的在前）
        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        print(f"\n总共获取 {len(all_news)} 条新闻（最近{months}个月）")
        return all_news
    
    def _crawl_page(self, url):
        """爬取单页新闻列表"""
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=15,
                verify=False
            )
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 查找新闻列表
            news_container = soup.select_one('ul.box04')
            if not news_container:
                print("  未找到新闻列表容器")
                return []
            
            # 查找所有新闻链接
            news_items = news_container.select('li a')
            
            for item in news_items:
                href = item.get('href', '')
                if not href or '/document/detail' not in href:
                    continue
                
                title = item.get_text(strip=True)
                if not title or len(title) < 5:
                    continue
                
                # 构建完整链接
                if href.startswith('/'):
                    full_url = self.base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = f"{self.base_url}/{href}"
                
                # 尝试从注释中提取日期
                date = ''
                parent_li = item.parent
                if parent_li:
                    # 查找被注释的日期
                    li_html = str(parent_li)
                    date_match = re.search(r'<!--\s*<span>(\d{4}-\d{2}-\d{2})</span>\s*-->', li_html)
                    if date_match:
                        date = date_match.group(1)
                
                # 避免重复
                if not any(n['link'] == full_url for n in news_list):
                    news_list.append({
                        'title': title,
                        'link': full_url,
                        'date': date,
                        'source': '深圳电子商会'
                    })
            
            return news_list
            
        except Exception as e:
            print(f"爬取页面时出错: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_news_detail(self, url):
        """获取新闻详情页的日期和内容"""
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15,
                verify=False
            )
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取日期
            date = ''
            # 尝试多种日期选择器
            date_selectors = [
                '.article-info',
                '.info',
                '.date',
                '.time',
                '.publish-time',
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    text = date_elem.get_text()
                    date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', text)
                    if date_match:
                        date = date_match.group(1).replace('/', '-')
                        # 补齐日期格式
                        parts = date.split('-')
                        if len(parts) == 3:
                            date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                        break
            
            # 如果还没找到日期，在整个页面中搜索
            if not date:
                page_text = soup.get_text()
                # 匹配常见日期格式
                date_patterns = [
                    r'(\d{4}年\d{1,2}月\d{1,2}日)',
                    r'(\d{4}-\d{1,2}-\d{1,2})',
                    r'(\d{4}/\d{1,2}/\d{1,2})',
                ]
                for pattern in date_patterns:
                    date_match = re.search(pattern, page_text)
                    if date_match:
                        date_str = date_match.group(1)
                        # 转换为标准格式
                        date_str = re.sub(r'年', '-', date_str)
                        date_str = re.sub(r'月', '-', date_str)
                        date_str = re.sub(r'日', '', date_str)
                        date_str = date_str.replace('/', '-')
                        parts = date_str.split('-')
                        if len(parts) == 3:
                            date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                        break
            
            # 提取内容
            content = ''
            content_selectors = [
                '#doc_content',
                '.textmain',
                '.article-content',
                '.content',
                '.detail-content',
                'article',
                '.main-content',
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 移除脚本和样式
                    for tag in content_elem.find_all(['script', 'style']):
                        tag.decompose()
                    
                    paragraphs = content_elem.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                        if content and len(content) > 50:
                            break
            
            return {
                'date': date,
                'content': content
            }
            
        except Exception as e:
            print(f"  获取详情页出错: {e}")
            return None
    
    def fetch_news_content(self, url):
        """
        获取新闻详情页的正文内容
        :param url: 新闻链接
        :return: 正文内容
        """
        detail = self._get_news_detail(url)
        if detail:
            return detail.get('content', '')
        return None
    
    def save_to_json(self, news_list, filename='seccw_news.json'):
        """保存新闻到 JSON 文件（三级嵌套格式）"""
        # 输出到 output 目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 三级嵌套格式：公司名称 -> 来源 -> 新闻列表
        data = {
            "行业新闻": {
                "深圳电子商会": [
                    {
                        'title': news.get('title', ''),
                        'link': news.get('link', ''),
                        'date': news.get('date', '')
                    }
                    for news in news_list
                ]
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"新闻已保存到: {filepath}")
        return filepath


def main():
    """主函数"""
    print("=" * 50)
    print("深圳电子商会新闻爬虫 (关键词: EDA)")
    print("=" * 50)
    
    crawler = SeccwNewsCrawler(keyword="EDA")
    
    # 爬取新闻（默认爬取5页，最近3个月）
    news_list = crawler.crawl(max_pages=5, months=3)
    
    if news_list:
        # 显示部分结果
        print("\n" + "=" * 50)
        print(f"爬取结果预览（前5条）：")
        print("=" * 50)
        
        for i, news in enumerate(news_list[:5], 1):
            print(f"\n{i}. {news['title']}")
            print(f"   日期: {news['date']}")
            print(f"   链接: {news['link']}")
        
        # 保存到 JSON
        crawler.save_to_json(news_list)
    else:
        print("\n未获取到任何新闻")


if __name__ == '__main__':
    main()
