# -*- coding: utf-8 -*-
"""
合见工软官网新闻爬虫
爬取 https://www.univista-isg.com/site/news 的新闻链接
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


class UnivistiaNewsCrawler:
    """合见工软官网新闻爬虫"""
    
    def __init__(self):
        self.base_url = "https://www.univista-isg.com"
        # 只爬取公司新闻板块 (catalog=12)
        self.news_url = "https://www.univista-isg.com/site/news?catalog=12"
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
                # 基础URL已有catalog参数，用&拼接分页参数
                url = f"{self.news_url}&Node_page={page}"
            
            news_list = self._crawl_page(url, is_first_page=(page == 1))
            
            if not news_list:
                print(f"第 {page} 页没有获取到新闻，停止爬取")
                break
            
            # 过滤日期（跳过没有日期或日期太旧的新闻，但不停止爬取）
            filtered_news = []
            has_old_news = False
            for news in news_list:
                news_date = news.get('date', '')
                if news_date and news_date >= cutoff_date:
                    filtered_news.append(news)
                elif news_date and news_date < cutoff_date:
                    has_old_news = True
            
            # 只有当普通新闻列表（非顶部特色新闻）中出现旧新闻时才停止
            # 通过检查是否有至少一半的新闻是旧的来判断
            if has_old_news and len(filtered_news) < len(news_list) // 2:
                stop_crawling = True
                print(f"  遇到大量超过{months}个月的新闻，停止爬取")
            
            all_news.extend(filtered_news)
            print(f"第 {page} 页获取 {len(filtered_news)} 条新闻（最近{months}个月）")
        
        # 按日期排序（最新的在前）
        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        print(f"\n总共获取 {len(all_news)} 条新闻（最近{months}个月）")
        return all_news
    
    def _crawl_page(self, url, is_first_page=False):
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
            
            # 如果是第一页，先处理顶部特色新闻
            if is_first_page:
                top_news = self._parse_top_news(soup)
                if top_news:
                    news_list.append(top_news)
            
            # 处理普通新闻列表
            news_items = soup.select('.news-item')
            
            for item in news_items:
                # 获取链接
                link_tag = item.find('a', href=True)
                if not link_tag:
                    continue
                
                href = link_tag.get('href', '')
                if not href:
                    continue
                
                # 获取标题
                title_elem = item.select_one('.title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                else:
                    continue
                
                if not title or len(title) < 5:
                    continue
                
                # 获取日期 (格式: YYYY-MM-DD)
                date = ''
                time_elem = item.select_one('.time')
                if time_elem:
                    date_text = time_elem.get_text(strip=True)
                    # 匹配 YYYY-MM-DD 格式
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                    if date_match:
                        date = date_match.group(1)
                
                # 构建完整链接
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = self.base_url + href
                else:
                    full_url = f"{self.base_url}/{href}"
                
                # 避免重复
                if not any(n['link'] == full_url for n in news_list):
                    news_list.append({
                        'title': title,
                        'link': full_url,
                        'date': date,
                        'source': '合见工软官网'
                    })
            
            return news_list
            
        except Exception as e:
            print(f"爬取页面时出错: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_top_news(self, soup):
        """解析顶部特色新闻"""
        try:
            top_section = soup.select_one('.news-top')
            if not top_section:
                return None
            
            # 获取链接
            link_tag = top_section.select_one('a.news-top-main')
            if not link_tag:
                return None
            
            href = link_tag.get('href', '')
            if not href:
                return None
            
            # 获取标题
            title_elem = top_section.select_one('.bottom .text p')
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                return None
            
            if not title or len(title) < 5:
                return None
            
            # 获取日期 (格式: MM-DD + YYYY)
            date = ''
            day_elem = top_section.select_one('.time .day')
            year_elem = top_section.select_one('.time .year')
            
            if day_elem and year_elem:
                day_text = day_elem.get_text(strip=True)  # 格式: MM-DD
                year_text = year_elem.get_text(strip=True)  # 格式: YYYY
                if day_text and year_text:
                    date = f"{year_text}-{day_text}"  # 拼接为 YYYY-MM-DD
            
            # 构建完整链接
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                full_url = self.base_url + href
            else:
                full_url = f"{self.base_url}/{href}"
            
            return {
                'title': title,
                'link': full_url,
                'date': date,
                'source': '合见工软官网'
            }
            
        except Exception as e:
            print(f"解析顶部新闻时出错: {e}")
            return None
    
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
            
            # 合见工软新闻详情页的内容选择器
            content_selectors = [
                '.article-content',
                '.news-content',
                '.content',
                '.news-detail',
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
    
    def save_to_json(self, news_list, filename='univista_news.json'):
        """保存新闻到 JSON 文件（三级嵌套格式）"""
        # 输出到 output 目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 三级嵌套格式：公司名称 -> 来源 -> 新闻列表
        data = {
            "合见工软": {
                "合见工软官网": [
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
    print("合见工软官网新闻爬虫")
    print("=" * 50)
    
    crawler = UnivistiaNewsCrawler()
    
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
