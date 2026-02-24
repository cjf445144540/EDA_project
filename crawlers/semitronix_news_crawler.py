# -*- coding: utf-8 -*-
"""
广立微官网新闻爬虫
爬取 https://www.semitronix.com/news/company-info/ 的新闻链接
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


class SemitronixNewsCrawler:
    """广立微官网新闻爬虫"""
    
    def __init__(self):
        self.base_url = "https://www.semitronix.com"
        self.news_url = "https://www.semitronix.com/news/company-info/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def crawl(self, max_pages=1, months=1):
        """
        爬取新闻列表
        :param max_pages: 最大爬取页数，默认1页
        :param months: 只保留最近几个月的新闻，默认1个月
        :return: 新闻列表
        """
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
        stop_crawling = False
        
        for page in range(1, max_pages + 1):
            if stop_crawling:
                break
                
            print(f"正在爬取第 {page} 页...")
            
            # 构建分页 URL
            if page == 1:
                url = self.news_url
            else:
                url = f"{self.news_url}?page={page}"
            
            news_list = self._crawl_page(url)
            
            if not news_list:
                print(f"第 {page} 页没有获取到新闻，停止爬取")
                break
            
            # 过滤日期
            filtered_news = []
            for news in news_list:
                news_date = news.get('date', '')
                if news_date and news_date >= cutoff_date:
                    filtered_news.append(news)
                elif news_date and news_date < cutoff_date:
                    # 新闻按时间倒序，遇到超过截止日期的新闻就停止
                    stop_crawling = True
                    print(f"  遇到超过{months}个月的新闻，停止爬取")
                    break
            
            all_news.extend(filtered_news)
            print(f"第 {page} 页获取 {len(filtered_news)} 条新闻（最近{months}个月）")
        
        print(f"\n总共获取 {len(all_news)} 条新闻（最近{months}个月）")
        return all_news
    
    def _crawl_page(self, url):
        """爬取单页新闻"""
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=15,
                verify=False  # 禁用 SSL 验证
            )
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 查找所有新闻链接（排除分页链接）
            news_links = soup.select('a[href*="/news/company-info/"]')
            
            for link in news_links:
                href = link.get('href', '')
                
                # 过滤掉非新闻链接（如分页链接、导航链接）
                if not href or not re.search(r'/news/company-info/\d+\.html', href):
                    continue
                
                # 获取标题
                title = link.get_text(strip=True)
                if not title or len(title) < 5:
                    continue
                
                # 从标题中提取日期并移除
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})$', title)
                if date_match:
                    date = date_match.group(1)
                    title = title.replace(date, '').strip()
                else:
                    date = self._extract_date(link)
                
                # 构建完整链接
                if href.startswith('/'):
                    full_url = self.base_url + href
                else:
                    full_url = href
                
                # 避免重复
                if not any(n['link'] == full_url for n in news_list):
                    news_list.append({
                        'title': title,
                        'link': full_url,
                        'date': date,
                        'source': '广立微官网'
                    })
            
            return news_list
            
        except Exception as e:
            print(f"爬取页面时出错: {e}")
            return []
    
    def _extract_date(self, link_element):
        """从链接元素附近提取日期"""
        # 尝试从父元素或兄弟元素中查找日期
        parent = link_element.parent
        if parent:
            text = parent.get_text()
            # 匹配日期格式 YYYY-MM-DD
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
            if date_match:
                return date_match.group(1)
        return ''
    
    def fetch_news_content(self, url):
        """
        获取新闻详情页的正文内容
        :param url: 新闻链接
        :return: 正文内容
        """
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
            
            # 广立微新闻详情页的内容选择器
            content_selectors = [
                '.article-content',
                '.news-content',
                '.content',
                'article',
                '.main-content',
            ]
            
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # 移除脚本和样式
                    for tag in content_div.find_all(['script', 'style']):
                        tag.decompose()
                    
                    paragraphs = content_div.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                        if content and len(content) > 50:
                            return content
            
            # 备用方案：提取 body 中的 p 标签
            body = soup.find('body')
            if body:
                paragraphs = body.find_all('p')
                texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
                if texts:
                    return '\n'.join(texts)
            
            return None
            
        except Exception as e:
            print(f"获取新闻内容时出错: {e}")
            return None
    
    def save_to_json(self, news_list, filename='semitronix_news.json'):
        """保存新闻到 JSON 文件（三级嵌套格式）"""
        # 输出到 json 目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 三级嵌套格式：公司名称 -> 来源 -> 新闻列表
        data = {
            "广立微": {
                "广立微官网": [
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
    print("广立微官网新闻爬虫")
    print("=" * 50)
    
    crawler = SemitronixNewsCrawler()
    
    # 爬取新闻（默认爬取前3页，最近1个月）
    news_list = crawler.crawl(max_pages=3, months=1)
    
    if news_list:
        # 显示部分结果
        print("\n" + "=" * 50)
        print("爬取结果预览（前5条）：")
        print("=" * 50)
        
        for i, news in enumerate(news_list[:5], 1):
            print(f"\n{i}. {news['title']}")
            print(f"   日期: {news['date']}")
            print(f"   链接: {news['link']}")
    else:
        print("\n未获取到任何新闻")
    
    # 无论是否有新闻都保存文件
    crawler.save_to_json(news_list)


if __name__ == "__main__":
    main()
