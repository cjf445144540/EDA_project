# -*- coding: utf-8 -*-
"""
全球半导体观察网站新闻爬虫
爬取 https://www.dramx.com 的EDA相关新闻
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import urllib3
from datetime import datetime, timedelta

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DramxNewsCrawler:
    """全球半导体观察新闻爬虫"""
    
    def __init__(self):
        self.base_url = "https://www.dramx.com"
        # EDA关键词页面
        self.list_url_template = "https://www.dramx.com/KeywordPost/2078/{page}.html"
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
            
            url = self.list_url_template.format(page=page)
            news_list = self._crawl_page(url)
            
            if not news_list:
                print(f"第 {page} 页没有获取到新闻，停止爬取")
                break
            
            # 按日期过滤
            filtered_news = []
            old_count = 0
            
            for news in news_list:
                news_date = news.get('date', '')
                if news_date and news_date >= cutoff_date:
                    filtered_news.append(news)
                elif news_date and news_date < cutoff_date:
                    old_count += 1
            
            # 如果大部分新闻都是旧的，停止爬取
            if old_count > len(news_list) // 2:
                stop_crawling = True
                print(f"  遇到大量超过{days}天的新闻，停止爬取")
            
            all_news.extend(filtered_news)
            print(f"第 {page} 页获取 {len(filtered_news)} 条新闻（最近{days}天）")
        
        # 按日期排序（最新的在前）
        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        print(f"\n总共获取 {len(all_news)} 条新闻（最近{days}天）")
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
            
            # 查找所有新闻容器
            news_containers = soup.select('div.Article-content')
            
            for container in news_containers:
                # 获取标题和链接
                title_elem = container.select_one('h3 > a')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                href = title_elem.get('href', '')
                
                if not title or not href:
                    continue
                
                # 构建完整链接
                if href.startswith('/'):
                    full_url = self.base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = f"{self.base_url}/{href}"
                
                # 获取日期
                date_elem = container.select_one('p.Article-date')
                date = date_elem.get_text(strip=True) if date_elem else ''
                
                # 避免重复
                if not any(n['link'] == full_url for n in news_list):
                    news_list.append({
                        'title': title,
                        'link': full_url,
                        'date': date,
                        'source': '全球半导体观察'
                    })
            
            return news_list
            
        except Exception as e:
            print(f"爬取页面时出错: {e}")
            import traceback
            traceback.print_exc()
            return []
    
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
            
            # 正文内容选择器
            content_selectors = [
                '.newspage-cont',
                '.News-content',
                '.article-content',
                '.content',
                'article',
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
                            return content
            
            return None
            
        except Exception as e:
            print(f"  获取详情页出错: {e}")
            return None
    
    def save_to_json(self, news_list, filename='dramx_news.json'):
        """保存新闻到 JSON 文件（三级嵌套格式）"""
        # 输出到 json 目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 三级嵌套格式
        data = {
            "行业新闻": {
                "全球半导体观察": [
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
    print("全球半导体观察新闻爬虫 (EDA)")
    print("=" * 50)
    
    crawler = DramxNewsCrawler()
    
    # 爬取新闻（默认1页，最近1个月）
    news_list = crawler.crawl(max_pages=1, days=7)
    
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
