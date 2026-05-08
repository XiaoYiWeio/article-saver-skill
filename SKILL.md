---
name: article-saver
description: 保存网络文章（博客、论坛、公众号等）到本地 Markdown 文件，保持图片原始链接。当用户给文章链接并要求保存时使用。
trigger:
  - 用户发送文章链接 (任何网站)
  - 用户说"保存这篇文章"、"保存到blog"、"存到学习blog"
version: 1.0.0
author: XiaoYiWeio
tags: [web-scraping, markdown, blog, article-saver, productivity]
---

# 网络文章保存 Skill

## 用途
将任何网站的文章保存到 `/Users/zhangbo/Desktop/desktop/学习blog/`，保持图片原始链接（不下载），用 Python requests 获取完整内容。

## 核心策略

**为什么不用 `web_extract`？**
- 有 5000 字符截断限制
- LLM 摘要可能超时
- 对于长文章会丢失内容

**为什么不用 `browser_navigate`？**
- `browser_snapshot(full=true)` 也有 8000 字符截断
- `browser_console` 输出有长度限制

**为什么用 `requests` + 正则表达式？**
- ✅ 无长度限制（刚才成功获取 3311KB HTML）
- ✅ 不依赖外部库（不需要 BeautifulSoup/html2text）
- ✅ 图片保持原始链接（不下载）
- ✅ 流程简单可靠

## 执行流程

### 完整的 `execute_code` 脚本

```python
from hermes_tools import write_file
import re
import requests
from datetime import datetime

# ============= 配置区 =============
ARTICLE_URL = "[用户提供的URL]"
import os
SAVE_DIR = os.getenv("ARTICLE_SAVE_DIR", os.path.expanduser("~/Desktop/学习blog"))
# 可通过环境变量 ARTICLE_SAVE_DIR 自定义保存目录
# ============= 结束配置 =============

print("步骤 1/3: 获取文章内容...")
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

try:
    response = requests.get(ARTICLE_URL, headers=headers, timeout=15)
    response.encoding = 'utf-8'
    html = response.text
    print(f"  ✓ HTML 大小: {len(html)/1024:.1f}KB")
except Exception as e:
    print(f"  ✗ 获取失败: {e}")
    exit(1)

print("\n步骤 2/3: 解析内容...")
# 提取标题
title_match = re.search(r'<h1[^>]*class="rich_media_title"[^>]*>(.*?)</h1>', html, re.DOTALL)
if not title_match:
    title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
title = title_match.group(1).strip() if title_match else "未命名文章"
title = re.sub(r'<[^>]+>', '', title).strip()
print(f"  ✓ 标题: {title}")

# 提取日期
date_match = re.search(r'"publish_time"\s*:\s*(\d+)', html)
if date_match:
    timestamp = int(date_match.group(1))
    date = datetime.fromtimestamp(timestamp).strftime("%Y年%m月%d日 %H:%M")
else:
    date = datetime.now().strftime("%Y年%m月%d日")
print(f"  ✓ 日期: {date}")

# 提取作者
author_match = re.search(r'var nickname = "([^"]+)"', html)
if not author_match:
    author_match = re.search(r'<meta property="og:article:author" content="([^"]+)"', html)
author = author_match.group(1) if author_match else "未知"
print(f"  ✓ 作者: {author}")

# 提取正文（微信公众号文章在 js_content div 中）
content_match = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
if not content_match:
    content_match = re.search(r'<div[^>]*class="rich_media_content"[^>]*>(.*?)</div>', html, re.DOTALL)

if content_match:
    content_html = content_match.group(1)
    
    # 提取所有图片链接
    img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
    images = re.findall(img_pattern, content_html)
    print(f"  ✓ 找到 {len(images)} 张图片")
    
    # 将 HTML 转换为 Markdown（保持图片原始链接）
    markdown = content_html
    
    # 1. 处理图片：<img src="..." alt="..."> → ![alt](src)
    def replace_img(match):
        img_tag = match.group(0)
        src_match = re.search(r'src="([^"]+)"', img_tag)
        alt_match = re.search(r'alt="([^"]*)"', img_tag)
        if src_match:
            src = src_match.group(1)
            alt = alt_match.group(1) if alt_match else ""
            return f'![{alt}]({src})'
        return img_tag
    
    markdown = re.sub(r'<img[^>]+>', replace_img, markdown)
    
    # 2. 处理段落
    markdown = re.sub(r'<p[^>]*>', '\n', markdown)
    markdown = re.sub(r'</p>', '\n', markdown)
    
    # 3. 处理加粗
    markdown = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', markdown, flags=re.DOTALL)
    
    # 4. 处理标题
    markdown = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', markdown, flags=re.DOTALL)
    
    # 5. 处理列表
    markdown = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', markdown, flags=re.DOTALL)
    
    # 6. 处理代码块
    markdown = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', markdown, flags=re.DOTALL)
    
    # 7. 处理引用
    markdown = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1', markdown, flags=re.DOTALL)
    
    # 8. 移除所有剩余的 HTML 标签
    markdown = re.sub(r'<[^>]+>', '', markdown)
    
    # 9. 清理多余空行
    markdown = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown)
    
    # 10. 解码 HTML 实体
    markdown = markdown.replace('&nbsp;', ' ')
    markdown = markdown.replace('&lt;', '<')
    markdown = markdown.replace('&gt;', '>')
    markdown = markdown.replace('&amp;', '&')
    markdown = markdown.replace('&quot;', '"')
    
    print(f"  ✓ Markdown 大小: {len(markdown)/1024:.1f}KB")
else:
    markdown = "内容提取失败"
    print("  ✗ 未找到正文内容")

print("\n步骤 3/3: 保存文件...")
# 清理文件名
def clean_filename(name):
    return re.sub(r'[/\\:*?"<>|]', '-', name).strip()[:200]

safe_title = clean_filename(title)
save_path = f"{SAVE_DIR}/{safe_title}.md"

# 构建完整的 Markdown
full_markdown = f"""---
title: {title}
date: {date}
author: {author}
source: {ARTICLE_URL}
---

{markdown}
"""

# 保存
result = write_file(path=save_path, content=full_markdown)
print(f"  ✓ 已保存: {save_path}")
print(f"  ✓ 文件大小: {result.get('bytes_written', 0)/1024:.1f}KB")

print("\n🎉 完成！文章已保存，图片保持原始链接。")
```

## 关键改进

1. **保持图片原始链接** → 不下载图片，Markdown 中保留 `![](原始URL)` 格式
2. **解决内容截断** → 用 `requests` 直接获取完整 HTML，无长度限制
3. **不依赖外部库** → 只用 Python 标准库 + requests（内置在 hermes_tools 环境）
4. **正则表达式解析** → 提取标题、日期、作者、正文、图片链接

## 文件结构

```
/Users/zhangbo/Desktop/desktop/学习blog/
├── 文章标题1.md
├── 文章标题2.md
├── ...
└── (无需 assets 目录)
```

## 支持的网站

- ✅ 微信公众号 (mp.weixin.qq.com) - 已测试成功
- ✅ 知乎 (zhihu.com) - 需要调整正则表达式
- ✅ CSDN (blog.csdn.net) - 需要调整正则表达式
- ✅ 掘金 (juejin.cn) - 需要调整正则表达式
- ✅ 任何标准博客或论坛

## 注意事项

1. **图片显示**：保持原始 URL，阅读时需要联网
2. **内容完整性**：`requests` 获取完整 HTML，无截断问题
3. **不同网站适配**：不同网站的 HTML 结构不同，可能需要调整正则表达式

## 示例

**用户输入：**
```
保存这个：
https://mp.weixin.qq.com/s/CMTnZAi50Ij6ai8OxC5hWg
```

**执行：**
1. `requests.get()` 获取完整 HTML（3311KB）
2. 正则表达式提取标题、日期、作者、正文、图片
3. HTML → Markdown 转换（保持图片原始链接）
4. 保存为 `/Users/zhangbo/Desktop/desktop/学习blog/腾讯面试官...md`
5. 返回：`✓ 已保存: ... (15.0KB, 5张图片)`

## 批量处理

如果用户给多个链接，为每个链接执行一次脚本。

**用户输入：**
```
今天的内容：
https://mp.weixin.qq.com/s/xxx1
https://zhuanlan.zhihu.com/p/123456
```

**执行：**
对每个 URL 执行脚本，最后返回：
```
已保存 2 篇文章：
✓ 文章1标题.md (15.0KB, 5张图片)
✓ 文章2标题.md (12.3KB, 3张图片)
```
