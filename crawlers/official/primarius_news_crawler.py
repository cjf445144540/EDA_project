# -*- coding: utf-8 -*-
"""
概伦电子官网新闻爬虫
爬取 https://www.primarius-tech.com/aboutus/news.html 的新闻链接
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


class PrimariusNewsCrawler:
    """概伦电子官网新闻爬虫"""
    
    def __init__(self):
        self.base_url = "https://www.primarius-tech.com"
        self.news_url = "https://www.primarius-tech.com/aboutus/news.html"
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
            
            # 构建分页 URL（概伦电子官网新闻页面似乎没有分页，只有一页）
            url = self.news_url
            
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
                    print(f"  遇到超过{days}天的新闻，停止爬取")
                    break
            
            all_news.extend(filtered_news)
            print(f"第 {page} 页获取 {len(filtered_news)} 条新闻（最近{days}天）")
        
        print(f"\n总共获取 {len(all_news)} 条新闻（最近{days}天）")
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
            
            # 查找新闻列表容器
            news_container = soup.find('ul', class_='news_list')
            if not news_container:
                print("  未找到新闻列表容器")
                return []
            
            # 查找所有新闻项
            news_items = news_container.find_all('li')
            
            for item in news_items:
                # 查找链接
                link_tag = item.find('a', href=True)
                if not link_tag:
                    continue
                
                href = link_tag.get('href', '')
                if not href:
                    continue
                
                # 获取标题
                title_elem = item.find('h3')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                else:
                    title = link_tag.get_text(strip=True)
                
                if not title or len(title) < 5:
                    continue
                
                # 提取日期（查找 li 中的日期元素）
                date = ''
                # 尝试多种方式提取日期
                date_elem = item.find(class_=lambda x: x and ('date' in x.lower() or 'time' in x.lower()))
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    date_match = re.search(r'(\d{4}[./]\d{1,2}[./]\d{1,2})', date_text)
                    if date_match:
                        date = date_match.group(1).replace('.', '-').replace('/', '-')
                        # 补齐月份和日期的前导零
                        parts = date.split('-')
                        if len(parts) == 3:
                            date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                
                # 如果没找到，尝试从整个 item 中提取（新闻日期在文本最后）
                if not date:
                    item_text = item.get_text()
                    # 匹配 YYYY.MM.DD 格式
                    date_match = re.search(r'(\d{4}[./]\d{1,2}[./]\d{1,2})', item_text)
                    if date_match:
                        date = date_match.group(1).replace('.', '-').replace('/', '-')
                        # 补齐月份和日期的前导零
                        parts = date.split('-')
                        if len(parts) == 3:
                            date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                
                # 构建完整链接
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = self.base_url + href
                else:
                    # 相对路径
                    full_url = f"{self.base_url}/aboutus/{href}"
                
                # 避免重复
                if not any(n['link'] == full_url for n in news_list):
                    news_list.append({
                        'title': title,
                        'link': full_url,
                        'date': date or '',
                        'source': '概伦电子官网'
                    })
            
            return news_list
            
        except Exception as e:
            print(f"爬取页面时出错: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_date(self, element):
        """从元素中提取日期"""
        try:
            # 尝试查找包含日期的元素
            date_patterns = [
                r'(\d{4}[-/]\d{2}[-/]\d{2})',
                r'(\d{4}年\d{1,2}月\d{1,2}日)',
            ]
            
            # 在当前元素及其子元素中查找
            text = element.get_text()
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    date_str = match.group(1)
                    # 统一格式为 YYYY-MM-DD
                    date_str = re.sub(r'年', '-', date_str)
                    date_str = re.sub(r'月', '-', date_str)
                    date_str = re.sub(r'日', '', date_str)
                    date_str = date_str.replace('/', '-')
                    
                    # 确保格式正确
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                        return date_str
                    except:
                        pass
            
            return ''
        except Exception:
            return ''
    
    def save_to_json(self, news_list, filename='primarius_news.json'):
        """保存新闻到 JSON 文件（三级嵌套格式）"""
        # 输出到 json/official 目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'json', 'official')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 三级嵌套格式：公司名称 -> 来源 -> 新闻列表
        data = {
            "概伦电子": {
                "概伦电子官网": [
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
    print("概伦电子官网新闻爬虫")
    print("=" * 50)
    
    crawler = PrimariusNewsCrawler()
    
    # 爬取新闻(默认爬取1页,最近1个月)
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
