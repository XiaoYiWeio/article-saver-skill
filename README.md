# Article Saver

保存网络文章到本地 Markdown 文件，保持图片原始链接。

## 功能特点

- ✅ 支持多种网站：微信公众号、知乎、CSDN、掘金等
- ✅ 转换为 Markdown 格式，本地阅读方便
- ✅ 保持图片原始链接，不占用本地空间
- ✅ 无长度限制，获取完整文章内容
- ✅ 自动提取标题、日期、作者信息
- ✅ 命令行参数支持，可自定义保存路径
- ✅ 智能识别不同网站，自动适配解析规则

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/XiaoYiWeio/article-saver-skill.git
cd article-saver-skill
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python article-saver.py "https://mp.weixin.qq.com/s/xxxxx"
```

### 指定保存目录

```bash
# 使用命令行参数
python article-saver.py "https://zhuanlan.zhihu.com/p/xxxxx" -o ~/Documents/articles

# 或设置环境变量
export ARTICLE_SAVE_DIR="/your/custom/path"
python article-saver.py "https://juejin.cn/post/xxxxx"
```

### 参数说明

```
positional arguments:
  url                  文章 URL

optional arguments:
  -h, --help          显示帮助信息
  -o, --dir DIR       保存目录路径
  -v, --version       显示版本信息
```

## 支持的网站

| 网站 | 网址 | 状态 |
|------|------|------|
| 微信公众号 | mp.weixin.qq.com | ✅ 已支持 |
| 知乎 | zhihu.com / 知乎专栏 | ✅ 已支持 |
| CSDN | blog.csdn.net | ✅ 已支持 |
| 掘金 | juejin.cn | ✅ 已支持 |
| 其他网站 | 通用解析 | ⚡ 部分支持 |

## 工作原理

1. 使用 `requests` 获取网页完整 HTML
2. 根据网站类型选择对应的解析规则
3. 正则表达式提取标题、日期、作者、正文
4. HTML 转换为 Markdown 格式
5. 保存到本地目录

## 项目结构

```
article-saver/
├── README.md          # 项目说明文档
├── SKILL.md           # Skill 配置文件
├── article-saver.py   # 主程序
└── requirements.txt   # Python 依赖
```

## 示例

### 保存微信公众号文章

```bash
python article-saver.py "https://mp.weixin.qq.com/s/CMTnZAi50Ij6ai8OxC5hWg"
```

输出：

```
步骤 1/4: 获取文章内容...
  ✓ HTML 大小: 3311.2KB

步骤 2/4: 解析内容...
  ✓ 标题: 文章标题
  ✓ 日期: 2024年01月15日 10:30
  ✓ 作者: 作者名称
  ✓ 找到 5 张图片

步骤 3/4: 转换为 Markdown...
  ✓ Markdown 大小: 15.0KB

步骤 4/4: 保存文件...
  ✓ 已保存: ~/Desktop/学习blog/文章标题.md
  ✓ 文件大小: 15.0KB

🎉 完成！文章已保存，图片保持原始链接。
```

## 注意事项

1. **图片显示**：保持原始 URL，阅读时需要联网
2. **内容完整性**：使用 requests 获取完整 HTML，无截断问题
3. **不同网站适配**：不同网站的 HTML 结构不同，已内置多种解析规则

## License

MIT License
