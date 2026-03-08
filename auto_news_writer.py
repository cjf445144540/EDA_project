# -*- coding: utf-8 -*-
"""
自动化新闻稿生成脚本
1. 读取 classified_news.json 的第一条新闻链接
2. 获取新闻正文内容
3. 生成提示词并复制到剪贴板
"""

import json
import requests
from bs4 import BeautifulSoup

# 尝试导入剪贴板库
try:
    import pyperclip
except ImportError:
    print("请先安装依赖库：pip install pyperclip")
    exit(1)


def get_first_news_link(json_file="classified_news.json"):
    """
    从 classified_news.json 获取第一条新闻的链接和标题
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 遍历找到第一条新闻
    for company_name, sources in data.items():
        for source_name, news_list in sources.items():
            if news_list:
                first_news = news_list[0]
                return {
                    "company_name": company_name,
                    "source": source_name,
                    "title": first_news.get("title", ""),
                    "link": first_news.get("link", ""),
                    "date": first_news.get("date", "")
                }
    
    return None


def clean_wechat_content(content, is_wechat=False):
    """
    清理微信公众号文章末尾的非新闻内容
    :param content: 原始内容
    :param is_wechat: 是否是微信公众号文章
    :return: 清理后的内容
    """
    if not content or not is_wechat:
        return content
    
    # 定义末尾需要去除的关键词（按段落匹配）
    footer_keywords = [
        '爆款好文',
        '温馨提示',
        '往期推荐',
        '精彩回顾',
        '热门文章',
        '推荐阅读',
        '相关阅读',
        '延伸阅读',
        '猜你喜欢',
        '更多精彩',
        '点击阅读',
        '长按识别',
        '扫码关注',
        '关注我们',
        '投稿邮箱',
        '商务合作',
        '联系我们',
        '免责声明',
        '版权声明',
        '声明：',
        '来源：',
        '编辑：',
        '责编：',
        '审核：'
    ]
    
    # 按段落分割内容
    paragraphs = content.split('\n')
    cleaned_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # 检查是否包含末尾关键词
        should_remove = False
        for keyword in footer_keywords:
            if keyword in para:
                should_remove = True
                break
        
        # 如果不包含关键词，保留该段落
        if not should_remove:
            cleaned_paragraphs.append(para)
        else:
            # 遇到第一个包含关键词的段落后，停止添加后续内容
            break
    
    return '\n'.join(cleaned_paragraphs)


def fetch_news_content(url):
    """
    从新闻链接获取新闻正文内容
    支持同花顺、广立微官网等多个来源
    """
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        
        # 根据URL判断编码
        if '10jqka.com' in url:
            response.encoding = 'gbk'
        else:
            response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return None
        
        html_text = response.text
        
        # 检查是否是跳转页面（跳转到微信公众号等）
        is_wechat_article = False
        if 'mp.weixin.qq.com' in html_text:
            import re
            # 提取微信公众号链接
            match = re.search(r"url:\s*['\"]?(https?://mp\.weixin\.qq\.com[^'\"\s]+)", html_text)
            if match:
                wx_url = match.group(1)
                print(f"  检测到跳转链接，尝试获取微信文章...")
                # 访问微信公众号文章
                try:
                    wx_response = requests.get(wx_url, headers=headers, timeout=15)
                    wx_response.encoding = 'utf-8'
                    if wx_response.status_code == 200:
                        html_text = wx_response.text
                        is_wechat_article = True
                except:
                    print("  微信文章获取失败")
        
        # 直接访问的微信链接
        if 'mp.weixin.qq.com' in url:
            is_wechat_article = True
        
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # 同花顺新闻正文的选择器
        content_selectors = [
            '.art-main-content',   # 主要文章内容
            '.atc-content',        # 文章内容
            '#main_content',       # 主内容
            '.main-text',          # 主文本
            '.article-content',    # 文章内容
            '.news-content',       # 新闻内容
            '#js_content',         # 微信公众号文章内容
            '.rich_media_content', # 微信公众号
            'article',             # article标签
        ]
        
        content = None
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # 移除脚本和样式标签
                for tag in content_div.find_all(['script', 'style']):
                    tag.decompose()
                
                # 提取所有段落文本
                paragraphs = content_div.find_all('p')
                if paragraphs:
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                else:
                    content = content_div.get_text(strip=True)
                
                if content and len(content) > 30:
                    break
        
        # 如果上面的选择器都没找到，尝试用body内的所有p标签
        if not content or len(content) < 30:
            body = soup.find('body')
            if body:
                paragraphs = body.find_all('p')
                texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
                if texts:
                    content = '\n'.join(texts[:5])  # 取前5个较长的段落
        
        # 清理微信公众号文章末尾的非新闻内容
        content = clean_wechat_content(content, is_wechat_article)
        
        return content
        
    except Exception as e:
        print(f"获取新闻内容时出错: {e}")
        return None


def copy_to_clipboard(content, title, source=""):
    """
    生成提示词并复制到剪贴板
    :param content: 新闻正文内容
    :param title: 新闻标题
    :param source: 新闻来源（如"同花顺"、"广立微官网"等）
    """
    # 超过5000字时截断
    MAX_CONTENT_LEN = 5000
    if content and len(content) > MAX_CONTENT_LEN:
        content = content[:MAX_CONTENT_LEN]

    # 判断是否是官网来源
    is_official_site = "官网" in source
    
    # 基础提示词
    prompt = f"""请根据以下新闻资讯，生成一篇新闻稿：

【原标题】{title}

【原文内容】
{content}

请生成一篇专业的新闻稿，要求：
1. 标题吸引人
2. 通过网络搜索补充更多信息
3. 将重点内容加粗显示
4. 每段首行缩进
5. 字数约800字
6. 将公司宣传性语言转化为事实陈述"""
    
    # 复制到剪贴板
    pyperclip.copy(prompt)
    
    return prompt


def main(news_url=None):
    """
    主函数
    :param news_url: 可选，直接传入新闻链接
    """
    print("=" * 60)
    print("自动化新闻稿生成脚本")
    print("=" * 60)
    
    news_info = None
    
    # 如果没有传入链接，询问用户
    if not news_url:
        print("\n请选择新闻来源：")
        print("1. 从 classified_news.json 读取第一条")
        print("2. 手动输入新闻链接")
        
        choice = input("\n请输入选择 (1/2)，直接回车默认选择1: ").strip()
        
        if choice == "2":
            news_url = input("请输入新闻链接: ").strip()
            if news_url:
                news_info = {
                    "title": "用户输入的新闻",
                    "link": news_url,
                    "company_name": "-",
                    "source": "-",
                    "date": "-"
                }
    else:
        # 直接使用传入的链接
        news_info = {
            "title": "外部传入的新闻",
            "link": news_url,
            "company_name": "-",
            "source": "-",
            "date": "-"
        }
    
    # 如果没有手动输入，从 JSON 读取
    if not news_info:
        print("\n[步骤1] 读取 classified_news.json...")
        news_info = get_first_news_link()
        
        if not news_info:
            print("错误：未找到任何新闻链接")
            return
    
    print(f"\n  公司名称: {news_info.get('company_name', '-')}")
    print(f"  新闻来源: {news_info.get('source', '-')}")
    print(f"  标题: {news_info.get('title', '-')}")
    print(f"  链接: {news_info['link']}")
    print(f"  日期: {news_info.get('date', '-')}")
    
    # 2. 获取新闻正文内容
    print("\n[步骤2] 获取新闻正文内容...")
    content = fetch_news_content(news_info['link'])
    
    if not content:
        print("警告：无法获取新闻正文，将使用标题作为内容")
        content = news_info['title']
    else:
        print(f"  成功获取正文，长度: {len(content)} 字符")
        # 截取前1500字符避免内容过长
        if len(content) > 1500:
            content = content[:1500] + "..."
    
    # 3. 生成提示词并复制到剪贴板
    print("\n[步骤3] 生成提示词并复制到剪贴板...")
    source = news_info.get('source', '')
    prompt = copy_to_clipboard(content, news_info['title'], source)
    
    # 显示是否添加了官网去主观化要求
    if "官网" in source:
        print(f"  ✅ 检测到官网来源 [{source}]，已添加去除主观描述的提示词")
    
    print("\n" + "=" * 60)
    print("✅ 提示词已复制到剪贴板！")
    print("=" * 60)
    print("\n提示词预览：")
    print("-" * 60)
    print(prompt[:300] + "..." if len(prompt) > 300 else prompt)


if __name__ == "__main__":
    import sys
    # 支持命令行传入链接
    if len(sys.argv) > 1:
        main(news_url=sys.argv[1])
    else:
        main()
