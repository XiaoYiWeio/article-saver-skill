#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Article Saver - 保存网络文章到本地 Markdown 文件
支持微信公众号、知乎、CSDN、掘金等网站
保持图片原始链接，无长度限制
"""

import os
import re
import sys
import argparse
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("错误: 请先安装 requests 库")
    print("运行: pip install requests")
    sys.exit(1)


DEFAULT_SAVE_DIR = os.path.expanduser("~/Desktop/学习blog")


def clean_filename(name):
    """清理文件名，移除非法字符"""
    return re.sub(r'[/\\:*?"<>|]', '-', name).strip()[:200]


def html_to_markdown(html_content):
    """将 HTML 内容转换为 Markdown 格式"""
    markdown = html_content

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
    markdown = re.sub(r'<p[^>]*>', '\n', markdown)
    markdown = re.sub(r'</p>', '\n', markdown)
    markdown = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1\n', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<br\s*/?>', '\n', markdown)
    markdown = re.sub(r'<[^>]+>', '', markdown)
    markdown = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown)

    entities = {
        '&nbsp;': ' ',
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
    }
    for entity, char in entities.items():
        markdown = markdown.replace(entity, char)

    return markdown.strip()


def extract_wechat_article(html):
    """提取微信公众号文章"""
    title_match = re.search(r'<h1[^>]*class="rich_media_title"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    title = title_match.group(1).strip() if title_match else "未命名文章"
    title = re.sub(r'<[^>]+>', '', title).strip()

    date_match = re.search(r'"publish_time"\s*:\s*(\d+)', html)
    if date_match:
        timestamp = int(date_match.group(1))
        date = datetime.fromtimestamp(timestamp).strftime("%Y年%m月%d日 %H:%M")
    else:
        date = datetime.now().strftime("%Y年%m月%d日")

    author_match = re.search(r'var nickname = "([^"]+)"', html)
    if not author_match:
        author_match = re.search(r'<meta property="og:article:author" content="([^"]+)"', html)
    author = author_match.group(1) if author_match else "未知"

    content_match = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
    if not content_match:
        content_match = re.search(r'<div[^>]*class="rich_media_content"[^>]*>(.*?)</div>', html, re.DOTALL)

    return title, date, author, content_match


def extract_zhihu_article(html):
    """提取知乎文章"""
    title_match = re.search(r'<h1[^>]*class="Post-Title"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    title = title_match.group(1).strip() if title_match else "未命名文章"
    title = re.sub(r'<[^>]+>', '', title).strip()

    date_match = re.search(r'"dateCreated"\s*:\s*"([^"]+)"', html)
    if date_match:
        date = date_match.group(1)[:10]
    else:
        date = datetime.now().strftime("%Y年%m月%d日")

    author_match = re.search(r'<span[^>]*class="Author-name"[^>]*>(.*?)</span>', html, re.DOTALL)
    if not author_match:
        author_match = re.search(r'<meta name="author" content="([^"]+)"', html)
    author = author_match.group(1).strip() if author_match else "未知"
    author = re.sub(r'<[^>]+>', '', author)

    content_match = re.search(r'<div[^>]*class="Post-RichText"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not content_match:
        content_match = re.search(r'<div[^>]*class="RichText"[^>]*>(.*?)</div>', html, re.DOTALL)

    return title, date, author, content_match


def extract_csdn_article(html):
    """提取 CSDN 文章"""
    title_match = re.search(r'<h1[^>]*class="article-title"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    title = title_match.group(1).strip() if title_match else "未命名文章"
    title = re.sub(r'<[^>]+>', '', title).strip()

    date_match = re.search(r'<span[^>]*class="time"[^>]*>(\d{4}-\d{2}-\d{2})</span>', html)
    if date_match:
        date = date_match.group(1).replace('-', '年', 1).replace('-', '月') + '日'
    else:
        date = datetime.now().strftime("%Y年%m月%d日")

    author_match = re.search(r'<a[^>]*class="follow-nickname"[^>]*>(.*?)</a>', html, re.DOTALL)
    if not author_match:
        author_match = re.search(r'<meta name="author" content="([^"]+)"', html)
    author = author_match.group(1).strip() if author_match else "未知"

    content_match = re.search(r'<div[^>]*id="content_views"[^>]*>(.*?)</div>', html, re.DOTALL)

    return title, date, author, content_match


def extract_juejin_article(html):
    """提取掘金文章"""
    title_match = re.search(r'<h1[^>]*class="article-title"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    title = title_match.group(1).strip() if title_match else "未命名文章"
    title = re.sub(r'<[^>]+>', '', title).strip()

    date_match = re.search(r'<time[^>]*datetime="([^"]+)"', html)
    if date_match:
        date = date_match.group(1)[:10].replace('-', '年', 1).replace('-', '月') + '日'
    else:
        date = datetime.now().strftime("%Y年%m月%d日")

    author_match = re.search(r'<span[^>]*class="author-name"[^>]*>(.*?)</span>', html, re.DOTALL)
    if not author_match:
        author_match = re.search(r'<meta name="author" content="([^"]+)"', html)
    author = author_match.group(1).strip() if author_match else "未知"
    author = re.sub(r'<[^>]+>', '', author)

    content_match = re.search(r'<div[^>]*class="article-content"[^>]*>(.*?)</div>', html, re.DOTALL)

    return title, date, author, content_match


def extract_generic_article(html):
    """提取通用文章（兜底方案）"""
    title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    title = title_match.group(1).strip() if title_match else "未命名文章"
    title = re.sub(r'<[^>]+>', '', title).strip()

    date = datetime.now().strftime("%Y年%m月%d日")

    author_match = re.search(r'<meta name="author" content="([^"]+)"', html)
    author = author_match.group(1) if author_match else "未知"

    main_content_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if not main_content_match:
        main_content_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    if not main_content_match:
        main_content_match = re.search(r'<div[^>]*class="content"[^>]*>(.*?)</div>', html, re.DOTALL)

    return title, date, author, main_content_match


def extract_article(html, url):
    """根据 URL 类型提取文章内容"""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    if 'mp.weixin.qq.com' in domain:
        return extract_wechat_article(html)
    elif 'zhihu.com' in domain:
        return extract_zhihu_article(html)
    elif 'blog.csdn.net' in domain:
        return extract_csdn_article(html)
    elif 'juejin.cn' in domain:
        return extract_juejin_article(html)
    else:
        return extract_generic_article(html)


def save_article(url, save_dir=None):
    """保存文章到本地"""
    save_dir = save_dir or os.environ.get('ARTICLE_SAVE_DIR', DEFAULT_SAVE_DIR)

    print("步骤 1/4: 获取文章内容...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding or 'utf-8'
        html = response.text
        print(f"  ✓ HTML 大小: {len(html)/1024:.1f}KB")
    except requests.RequestException as e:
        print(f"  ✗ 获取失败: {e}")
        return False

    print("\n步骤 2/4: 解析内容...")
    title, date, author, content_match = extract_article(html, url)
    print(f"  ✓ 标题: {title}")
    print(f"  ✓ 日期: {date}")
    print(f"  ✓ 作者: {author}")

    if not content_match:
        print("  ✗ 未找到正文内容")
        return False

    content_html = content_match.group(1)

    img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
    images = re.findall(img_pattern, content_html)
    print(f"  ✓ 找到 {len(images)} 张图片")

    print("\n步骤 3/4: 转换为 Markdown...")
    markdown_content = html_to_markdown(content_html)
    print(f"  ✓ Markdown 大小: {len(markdown_content)/1024:.1f}KB")

    print("\n步骤 4/4: 保存文件...")
    os.makedirs(save_dir, exist_ok=True)

    safe_title = clean_filename(title)
    save_path = os.path.join(save_dir, f"{safe_title}.md")

    counter = 1
    while os.path.exists(save_path):
        save_path = os.path.join(save_dir, f"{safe_title}_{counter}.md")
        counter += 1

    full_markdown = f"""---
title: {title}
date: {date}
author: {author}
source: {url}
---

{markdown_content}
"""

    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(full_markdown)
        file_size = os.path.getsize(save_path)
        print(f"  ✓ 已保存: {save_path}")
        print(f"  ✓ 文件大小: {file_size/1024:.1f}KB")
        return True
    except IOError as e:
        print(f"  ✗ 保存失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Article Saver - 保存网络文章到本地 Markdown 文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python article-saver.py "https://mp.weixin.qq.com/s/xxxxx"
  python article-saver.py "https://zhuanlan.zhihu.com/p/xxxxx" -o ~/Documents/articles
  python article-saver.py "https://juejin.cn/post/xxxxx" --dir "/path/to/save"
        """
    )
    parser.add_argument('url', nargs='?', help='文章 URL')
    parser.add_argument('-o', '--dir', dest='save_dir', help='保存目录路径')
    parser.add_argument('-v', '--version', action='version', version='Article Saver v1.0.0')

    args = parser.parse_args()

    if not args.url:
        parser.print_help()
        print("\n错误: 请提供文章 URL")
        sys.exit(1)

    success = save_article(args.url, args.save_dir)

    if success:
        print("\n🎉 完成！文章已保存，图片保持原始链接。")
        sys.exit(0)
    else:
        print("\n❌ 保存失败，请检查 URL 是否正确或网络连接。")
        sys.exit(1)


if __name__ == '__main__':
    main()
