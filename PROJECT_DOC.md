# EDA新闻爬虫系统 - 工程文档

## 一、项目概述

本项目是一个自动化的EDA行业新闻采集系统，从多个新闻源爬取新闻，经过分类筛选后输出结构化数据。

**GitHub仓库**: https://github.com/cjf445144540/EDA_project.git

---

## 二、目录结构

```
EDA自媒体/
├── run_crawler.py          # 主入口脚本，统一调度所有爬虫
├── classify_news.py        # 新闻分类器
├── auto_news_writer.py     # 新闻内容获取与剪贴板工具
├── crawlers/               # 行业/媒体新闻爬虫
│   ├── __init__.py
│   ├── stock_news_crawler.py      # 同花顺个股新闻
│   ├── dramx_news_crawler.py      # 全球半导体观察
│   ├── seccw_news_crawler.py      # 深圳电子商会
│   ├── eetimes_news_crawler.py    # EETimes
│   ├── sina_news_crawler.py       # 新浪网
│   ├── qq_news_crawler.py         # 腾讯网
│   ├── sohu_news_crawler.py       # 搜狐网
│   └── official/           # 公司官网爬虫
│       ├── __init__.py
│       ├── semitronix_news_crawler.py   # 广立微官网
│       ├── primarius_news_crawler.py    # 概伦电子官网
│       ├── univista_news_crawler.py     # 合见工软官网
│       ├── xepic_news_crawler.py        # 芯华章官网
│       ├── s2c_news_crawler.py          # 思尔芯官网
│       ├── gigada_news_crawler.py       # 鸿芯微纳官网
│       ├── xpeedic_news_crawler.py      # 芯和半导体官网
│       ├── synopsys_news_crawler.py     # Synopsys (SemiWiki/Design-Reuse)
│       ├── cadence_news_crawler.py      # Cadence (SemiWiki/Design-Reuse)
│       └── siemens_news_crawler.py      # Siemens (SemiWiki/Design-Reuse)
├── json/                   # 行业新闻JSON输出
│   ├── official/           # 官网新闻JSON输出
│   ├── ths_*.json          # 同花顺新闻
│   ├── classified_news.json # 最终分类结果
│   └── batch_news_results.json # 原始爬取结果
└── result/                 # 结果目录（预留）
```

---

## 三、爬虫配置汇总

全局默认配置：`DEFAULT_DAYS=7`、`DEFAULT_MAX_PAGES=1`、`DEFAULT_MIN_CONTENT_LENGTH=500`

| 爬虫 | 启用状态 | 来源类型 | 关键词/目标 | 时效 | 页数 |
|------|----------|----------|-------------|------|------|
| 同花顺 | 启用 | 个股新闻 | 301269/688206/301095 | 7天 | - |
| 广立微官网 | 启用 | 公司官网 | 公司新闻板块 | 7天 | 1页 |
| 概伦电子官网 | 启用 | 公司官网 | 公司新闻板块 | 7天 | 1页 |
| 合见工软官网 | 启用 | 公司官网 | 公司新闻(catalog=12) | 7天 | 1页 |
| 芯华章官网 | 启用 | 公司官网 | 公司新闻板块 | 7天 | 1页 |
| 思尔芯官网 | 启用 | 公司官网 | 公司新闻板块 | 7天 | 1页 |
| 鸿芯微纳官网 | 启用 | 公司官网 | 公司新闻板块 | 7天 | 1页 |
| 芯和半导体官网 | 启用 | 公司官网 | 公司新闻板块 | 7天 | 1页 |
| Synopsys | 启用 | 行业媒体 | SemiWiki + Design-Reuse | 7天 | 1页 |
| Cadence | 启用 | 行业媒体 | SemiWiki + Design-Reuse | 7天 | 1页 |
| Siemens | 启用 | 行业媒体 | SemiWiki + Design-Reuse | 7天 | 1页 |
| 全球半导体观察 | 启用 | 行业媒体 | EDA关键词 | 7天 | 1页 |
| 深圳电子商会 | 启用 | 行业媒体 | EDA搜索 | 7天 | 1页 |
| EETimes | 启用 | 行业媒体 | synopsys/cadence/siemens/EDA | 7天 | 1页 |
| 新浪网 | 启用 | 综合门户 | EDA搜索 | 7天 | 1页 |
| 腾讯网 | 启用 | 综合门户 | EDA搜索 | 7天 | 1页 |
| 搜狐网 | 启用 | 综合门户 | EDA搜索 | 7天 | 1页 |
| 电子工程网 | 关闭 | 行业媒体 | EDA搜索 | 7天 | 1页 |
| 电子工程专辑 | 启用 | 行业媒体 | eda搜索 | 7天 | 1页 |
| 电子工程世界 | 关闭 | 行业媒体 | EDA搜索 | 7天 | 1页 |

---

## 四、新闻筛选规则

### 4.1 筛选流程

```
爬取新闻 → 分类筛选 → 标题去重 → 内容检查与正文获取 → 最终列表过滤(>=200字) → 输出
```

### 4.2 分类关键词

新闻按以下关键词分为多个类别，**只保留以下四类**：

| 分类 | 关键词 |
|------|--------|
| **财务相关** | 业绩、财报、季报、年报、营收、利润、盈利、亏损、分红、派息 |
| **战略合作** | 合作、协议、签署、战略、合资、并购、收购 |
| **技术研发** | 研发、技术、专利、创新、产品、芯片、EDA、AI、人工智能、仿真、验证、设计、方案、平台 |
| **行业分析** | 行业、市场、分析、研报、点评、投资、峰会 |

### 4.3 来源筛选策略

不同来源采用不同的筛选策略：

| 策略 | 适用来源 | 规则说明 |
|------|----------|----------|
| **跳过筛选** | EETimes | 已用关键词搜索，直接保留所有结果 |
| **仅分类筛选** | 国内公司官网、全球半导体观察、深圳电子商会、新浪、腾讯、搜狐 | 只检查是否属于四类，不要求标题含公司名 |
| **仅公司相关** | SemiWiki、Design-Reuse、Synopsys官网、Cadence官网、Siemens官网 | 只检查标题是否含公司名(如Synopsys)，不做分类筛选 |
| **双重筛选** | 同花顺 | 需同时满足：属于四类 + 标题含公司名 |

### 4.4 各来源详细筛选规则

#### 同花顺个股新闻
- **目标股票**: 华大九天(301269)、概伦电子(688206)、广立微(301095)
- **筛选规则**: 分类筛选(四类) + 公司名称匹配
- **特殊处理**: 微信跳转文章使用section标签提取内容

#### 国内EDA公司官网
| 公司 | 爬取板块 | 筛选规则 |
|------|----------|----------|
| 广立微 | 新闻动态 | 仅分类筛选 |
| 概伦电子 | 新闻动态 | 仅分类筛选 |
| 合见工软 | 公司新闻(catalog=12) | 仅分类筛选 |
| 芯华章 | 新闻动态 | 仅分类筛选 |
| 思尔芯 | 新闻动态 | 仅分类筛选 |
| 鸿芯微纳 | 新闻动态 | 仅分类筛选 |
| 芯和半导体 | 新闻动态 | 仅分类筛选 |

#### 国外EDA三巨头
| 公司 | 新闻来源 | 筛选规则 |
|------|----------|----------|
| Synopsys | SemiWiki + Design-Reuse | 仅公司名称匹配(标题含Synopsys) |
| Cadence | SemiWiki + Design-Reuse | 仅公司名称匹配(标题含Cadence) |
| Siemens | SemiWiki + Design-Reuse | 仅公司名称匹配(标题含Siemens) |

#### EETimes
- **搜索关键词**: synopsys, cadence, siemens, EDA
- **标题过滤**: 只保留标题包含关键词的新闻
- **筛选规则**: 跳过分类筛选，直接保留

#### 综合门户(新浪/腾讯/搜狐)
- **搜索关键词**: EDA
- **筛选规则**: 仅分类筛选(四类)
- **爬虫内内容过滤**: ≥500字
- **特殊处理**: 
  - 腾讯：从URL提取日期(格式/a/20260310A...)
  - 搜狐：支持ODIN API + 页面爬取双引擎

#### 电子工程三家（电子工程网/电子工程专辑/电子工程世界）
- **筛选规则**: 仅分类筛选(四类)
- **爬虫内内容过滤**: `min_content_length`（当前默认500）
- **正文获取策略**: `requests` 优先，失败回退 Selenium
- **最终阶段共享规则**: 进入最终候选列表前统一要求正文字数 ≥200

---

## 五、内容获取规则

### 5.1 内容长度过滤
- 爬虫内默认最小字数: **500字**（由 `DEFAULT_MIN_CONTENT_LENGTH` 控制）
- 最终列表阶段统一阈值: **200字**（run_crawler 主流程共享规则）
- 低于对应阈值的新闻会在相应阶段被过滤

### 5.2 特殊内容处理

| 场景 | 处理方式 |
|------|----------|
| 微信公众号文章 | 使用`#js_content`选择器，get_text提取(内容在section标签) |
| 同花顺跳转微信 | 检测`mp.weixin.qq.com`，跟踪跳转获取内容 |
| 直播类新闻 | 标题含"直播"关键词的新闻被过滤 |

### 5.3 日期提取

| 来源 | 日期提取方式 |
|------|--------------|
| 腾讯网 | 从URL提取(格式:/a/20260310A...) |
| 搜狐网 | 从页面文本提取(支持相对时间、YYYY-MM-DD、M月D日) |
| 其他 | 从页面元素提取 |

### 5.4 电子工程来源正文通道
| 来源 | 正文获取策略 |
|------|--------------|
| 电子工程网 | requests 优先，失败回退 Selenium |
| 电子工程专辑 | requests 优先，失败回退 Selenium |
| 电子工程世界 | requests 优先，失败回退 Selenium（列表抓取同样支持该双通道） |

---

## 六、输出格式

### 6.1 最终分类结果 (classified_news.json)

```json
{
  "华大九天": {
    "同花顺": [
      {
        "title": "新闻标题",
        "link": "https://...",
        "date": "2026-03-11"
      }
    ]
  },
  "行业新闻": {
    "新浪网": [...],
    "腾讯网": [...]
  }
}
```

### 6.2 去重规则
- 跨来源标题去重
- 相同标题只保留第一条

---

## 七、运行配置

### 7.1 并行执行
- 爬虫并行线程数: **10**
- 内容获取并行线程数: **10**

### 7.2 运行命令

```bash
# 运行主脚本（爬取+分类+获取内容）
python run_crawler.py

# 单独运行分类
python classify_news.py
```

---

## 八、技术要点

### 8.1 依赖库
- requests: HTTP请求
- BeautifulSoup: HTML解析
- selenium: 动态页面爬取与回退通道（腾讯/搜狐/电子工程三家等）
- playwright: 动态页面爬取（腾讯/搜狐备选通道）
- pyperclip: 剪贴板操作

### 8.2 反爬处理
- User-Agent模拟
- 禁用代理: `proxies={'http': None, 'https': None}`
- SSL警告禁用
- 重试机制(3次)

### 8.3 SPA页面处理
- 优先使用Playwright
- 失败时fallback到Selenium
- 支持等待页面加载完成

---

## 九、配置修改指南

### 9.1 修改时效范围
在`run_crawler.py`中修改各爬虫的`days`参数：
```python
SINA_CONFIG = {
    'days': 7,  # 修改为需要的天数
}
```

### 9.2 添加新爬虫
1. 在`crawlers/`或`crawlers/official/`创建爬虫文件
2. 在`crawlers/__init__.py`添加导入
3. 在`run_crawler.py`添加配置和运行函数
4. 在筛选策略列表中添加来源名称

### 9.3 修改筛选规则
在`run_crawler.py`的main函数中修改：
```python
target_categories = ["财务相关", "战略合作", "技术研发", "行业分析"]
skip_sources = ["EETimes"]
category_only_sources = [...]
company_only_sources = [...]
```


*文档更新时间: 2026-03-22*
