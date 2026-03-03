# -*- coding: utf-8 -*-
"""
芯华章官网新闻爬虫
爬取 https://www.x-epic.com/index.html#/zh/media 的新闻链接
通过 API 接口获取新闻数据
"""

import requests
import json
import os
import re
import urllib3
from datetime import datetime, timedelta

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XepicNewsCrawler:
    """芯华章官网新闻爬虫"""
    
    def __init__(self):
        self.base_url = "https://www.x-epic.com"
        # API 接口地址（参数在URL中传递）
        self.api_url = "https://www.x-epic.com/api/xepic/publishContent/findPage"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://www.x-epic.com',
            'Referer': 'https://www.x-epic.com/index.html',
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
        page_size = 10  # 每页获取10条
        
        for page in range(1, max_pages + 1):
            if stop_crawling:
                break
                
            print(f"正在爬取第 {page} 页...")
            
            news_list = self._fetch_page(page, page_size)
            
            if not news_list:
                print(f"第 {page} 页没有获取到新闻，停止爬取")
                break
            
            # 过滤日期
            filtered_news = []
            has_old_news = False
            for news in news_list:
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
    
    def _fetch_page(self, page, size):
        """通过 API 获取单页新闻"""
        try:
            # URL 带分页参数
            url = f"{self.api_url}?current={page}&size={size}"
            
            # POST 请求体：busiType=10 表示公司动态
            payload = {
                "busiType": 10,
                "xeLanguage": "zh_CN"
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=15,
                verify=False
            )
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return []
            
            data = response.json()
            
            # 解析返回数据 (code=0 表示成功)
            if data.get('code') != 0:
                print(f"API返回错误: {data.get('message', '未知错误')}")
                return []
            
            records = data.get('data', {}).get('records', [])
            news_list = []
            
            for record in records:
                # 提取新闻信息
                title = record.get('title', '').strip()
                if not title or len(title) < 5:
                    continue
                
                # 提取日期：优先使用 viewDate，其次 publishTime
                date = ''
                view_date = record.get('viewDate', '')
                publish_time = record.get('publishTime', '') or record.get('createTime', '')
                
                if view_date:
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', view_date)
                    if date_match:
                        date = date_match.group(1)
                elif publish_time:
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', publish_time)
                    if date_match:
                        date = date_match.group(1)
                
                # 构建新闻链接
                news_id = record.get('id', '')
                rel_language_id = record.get('relLanguageId', '')
                if news_id:
                    # SPA 应用的新闻详情链接格式
                    # 格式: #/zh/media/detail?id={id}&l=zh_CN&rId={relLanguageId}
                    full_url = f"{self.base_url}/index.html#/zh/media/detail?id={news_id}&l=zh_CN"
                    if rel_language_id:
                        full_url += f"&rId={rel_language_id}"
                else:
                    continue
                
                # 获取新闻正文内容（body 字段包含 HTML 内容）
                body_content = record.get('body', '') or record.get('description', '')
                clean_content = ''
                if body_content:
                    # 移除 HTML 标签
                    clean_content = re.sub(r'<[^>]+>', '', body_content)
                    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                
                news_list.append({
                    'title': title,
                    'link': full_url,
                    'date': date,
                    'source': '芯华章官网',
                    'content': clean_content  # 保存内容
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
            # 从 URL 中提取新闻 ID
            id_match = re.search(r'id=([a-f0-9]+)', url)
            if not id_match:
                return None
            
            target_id = id_match.group(1)
            
            # 从列表 API 获取内容（body 字段包含完整内容）
            api_url = f"{self.base_url}/api/xepic/publishContent/findPage?current=1&size=50"
            payload = {"busiType": 10, "xeLanguage": "zh_CN"}
            
            response = requests.post(
                api_url,
                headers=self.headers,
                json=payload,
                timeout=15,
                verify=False
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if data.get('code') != 0:
                return None
            
            # 查找匹配的新闻
            records = data.get('data', {}).get('records', [])
            for record in records:
                if record.get('id') == target_id:
                    content = record.get('body', '')
                    if content:
                        # 移除 HTML 标签
                        clean_content = re.sub(r'<[^>]+>', '', content)
                        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                        return clean_content
            
            return None
            
        except Exception as e:
            print(f"获取新闻内容时出错: {e}")
            return None
    
    def save_to_json(self, news_list, filename='xepic_news.json'):
        """保存新闻到 JSON 文件（三级嵌套格式）"""
        # 输出到 output 目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 三级嵌套格式：公司名称 -> 来源 -> 新闻列表
        data = {
            "芯华章": {
                "芯华章官网": [
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
    print("芯华章官网新闻爬虫")
    print("=" * 50)
    
    crawler = XepicNewsCrawler()
    
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
