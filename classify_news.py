# -*- coding: utf-8 -*-
"""
新闻分类脚本
根据标题关键词对爬取的新闻进行分类
"""

import json
import os
from collections import defaultdict

class NewsClassifier:
    """新闻分类器"""
    
    def __init__(self):
        """初始化分类规则"""
        # 定义分类关键词字典
        self.categories = {
            "财务相关": ["业绩", "财报", "季报", "年报", "营收", "利润", "盈利", "亏损", "分红", "派息"],
            "融资融券": ["融资", "融券", "买入", "卖出", "减持", "增持"],
            "股东变动": ["股东", "持股", "减持", "增持", "解禁", "质押"],
            "公司公告": ["公告", "决议", "会议", "股东大会", "董事会", "监事会"],
            "战略合作": ["合作", "协议", "签署", "战略", "合资", "并购", "收购"],
            "技术研发": ["研发", "技术", "专利", "创新", "产品", "芯片", "EDA", "AI", "人工智能", "仿真", "验证", "设计", "方案", "平台"],
            "行业分析": ["行业", "市场", "分析", "研报", "点评", "投资", "峰会"],
            "人事变动": ["高管", "任命", "辞职", "变动", "董事", "总裁", "CEO"],
            "监管处罚": ["处罚", "违规", "整改", "问询", "调查", "立案"],
            "其他新闻": []  # 兖底分类
        }
        
        # 股票代码对应的公司名称映射
        self.stock_names = {
            "301269": ["华大九天"],
            "688206": ["概伦电子", "概伦"],
            "301095": ["广立微"],
        }
    
    def is_company_related(self, title, stock_code):
        """
        检查标题是否包含指定股票的公司名称
        :param title: 新闻标题
        :param stock_code: 股票代码
        :return: True/False
        """
        company_names = self.stock_names.get(stock_code, [])
        for name in company_names:
            if name in title:
                return True
        return False
    
    def classify_single_news(self, title):
        """
        对单条新闻标题进行分类
        :param title: 新闻标题
        :return: 分类名称
        """
        title_lower = title.lower()  # 转小写进行匹配
        # 遍历所有分类
        for category, keywords in self.categories.items():
            if category == "其他新闻":
                continue
            # 检查标题是否包含该分类的关键词（不区分大小写）
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    return category
        
        # 如果没有匹配到任何分类，归为"其他新闻"
        return "其他新闻"
    
    def classify_batch(self, news_data, filter_categories=None, only_company_related=False, skip_filter_sources=None, category_only_sources=None, company_only_sources=None):
        """
        批量分类新闻
        :param news_data: 新格式：公司名称 -> 来源 -> 新闻列表
        :param filter_categories: 需要保留的分类列表，None表示保留所有
        :param only_company_related: 是否只保留公司直接相关的新闻
        :param skip_filter_sources: 跳过分类筛选的来源列表，这些来源的新闻直接保留
        :param category_only_sources: 只做分类筛选的来源列表，不限公司相关
        :param company_only_sources: 只做公司相关筛选的来源列表，不做分类筛选
        :return: 三级嵌套格式：公司名称 -> 来源 -> 新闻列表
        """
        classified_results = {}
        skip_sources = skip_filter_sources or []
        category_only = category_only_sources or []
        company_only = company_only_sources or []
        
        for company_name, sources in news_data.items():
            # 按来源分组的结果
            sources_dict = defaultdict(list)
            
            # 遍历每个来源
            for source_name, news_list in sources.items():
                # 对每条新闻进行分类
                for news_item in news_list:
                    title = news_item.get("title", "")
                    
                    # 准备新闻项（不包含source字段）
                    news_output = {
                        'title': news_item.get('title', ''),
                        'link': news_item.get('link', ''),
                        'date': news_item.get('date', ''),
                        'content': news_item.get('content', '')
                    }
                    
                    # 如果是跳过筛选的来源，直接保留
                    if source_name in skip_sources:
                        sources_dict[source_name].append(news_output)
                        continue
                    
                    # 否则进行分类筛选
                    category = self.classify_single_news(title)
                    is_company = self._check_company_in_title(title, company_name)
                    
                    # 判断是否符合筛选条件
                    should_include = False
                    
                    # 如果是只做公司相关筛选的来源（不做分类筛选）
                    if source_name in company_only:
                        if is_company:
                            should_include = True
                    # 如果是只做分类筛选的来源
                    elif source_name in category_only:
                        if filter_categories is None or category in filter_categories:
                            should_include = True
                    # 如果要求公司直接相关
                    elif only_company_related:
                        # 只保留公司直接相关的新闻（需要同时满足分类条件）
                        if (filter_categories is None or category in filter_categories) and is_company:
                            should_include = True
                    else:
                        # 按原来的过滤逻辑
                        if filter_categories is None or category in filter_categories:
                            should_include = True
                    
                    if should_include:
                        sources_dict[source_name].append(news_output)
            
            # 只有当该公司有符合条件的新闻时才添加到结果中
            if sources_dict:
                classified_results[company_name] = dict(sources_dict)
        
        return classified_results
    
    def _check_company_in_title(self, title, company_name):
        """检查标题中是否包含公司名称（不区分大小写）"""
        if not title or not company_name:
            return False
        return company_name.lower() in title.lower()
    
    def save_classified_results(self, classified_data, output_file="classified_news.json"):
        """
        保存分类结果到文件
        :param classified_data: 分类后的数据
        :param output_file: 输出文件名
        """
        # 输出到 json 目录
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, output_file)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(classified_data, f, ensure_ascii=False, indent=2)
        print(f"分类结果已保存到: {filepath}")
    
    def print_summary(self, classified_data):
        """
        打印分类统计摘要
        :param classified_data: 三级嵌套格式：公司名称 -> 来源 -> 新闻列表
        """
        print("\n" + "="*60)
        print("新闻分类统计摘要")
        print("="*60)
        
        for company_name, sources in classified_data.items():
            total_count = sum(len(news_list) for news_list in sources.values())
            print(f"\n【{company_name}】")
            print(f"  总新闻数: {total_count} 条")
            print(f"  来源统计:")
            
            for source_name, news_list in sources.items():
                print(f"    - {source_name}: {len(news_list)} 条")


def main():
    """主函数"""
    # 1. 读取爬取结果
    json_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json')
    input_file = os.path.join(json_dir, "batch_news_results.json")
    
    if not os.path.exists(input_file):
        print(f"错误: 找不到文件 {input_file}")
        print("请先运行 run_crawler.py 爬取新闻数据")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    # 2. 创建分类器并执行分类（只保留指定的四类）
    classifier = NewsClassifier()
    target_categories = ["财务相关", "战略合作", "技术研发", "行业分析"]
    classified_results = classifier.classify_batch(news_data, filter_categories=target_categories)
    
    print(f"\n过滤规则: 只保留 {', '.join(target_categories)} 四类新闻")
    
    # 3. 保存分类结果
    classifier.save_classified_results(classified_results)
    
    # 4. 打印统计摘要
    if classified_results:
        classifier.print_summary(classified_results)
    else:
        print("\n[!] 警告: 所有股票的新闻都被过滤掉了，没有符合条件的新闻")
    
    # 5. 打印详细分类结果示例
    if classified_results:
        print("\n" + "="*60)
        print("详细分类示例 (仅显示前3条)")
        print("="*60)
        
        for company_name, data in classified_results.items():
            print(f"\n【{company_name}】")
            for category, news_list in data['categories'].items():
                if news_list:  # 只显示有新闻的分类
                    print(f"\n  [{category}] ({len(news_list)}条)")
                    for i, news in enumerate(news_list[:3], 1):  # 只显示前3条
                        print(f"    {i}. {news['title']}")
                        print(f"       来源: {news.get('source', '-')}")
                        print(f"       链接: {news['link']}")
                    if len(news_list) > 3:
                        print(f"    ... 还有 {len(news_list) - 3} 条")


if __name__ == "__main__":
    main()
