# Article Saver

保存网络文章到本地 Markdown 文件，保持图片原始链接。

## 功能特点

- ✅ 支持保存微信公众号、知乎、CSDN、掘金等网站文章
- ✅ 转换为 Markdown 格式，本地阅读
- ✅ 保持图片原始链接，不占用本地空间
- ✅ 无长度限制，获取完整文章内容
- ✅ 自动提取标题、日期、作者信息

## 使用方法

### 安装依赖

```bash
pip install requests
```

### 配置保存路径

编辑 `article-saver.py` 中的 `SAVE_DIR`：
```python
SAVE_DIR = "/your/custom/path"
```

或设置环境变量：
```bash
export ARTICLE_SAVE_DIR="/your/custom/path"
```

### 运行

```bash
python article-saver.py "https://example.com/article-url"
```

## 工作原理

1. 使用 `requests` 获取网页完整 HTML
2. 正则表达式提取标题、日期、作者、正文
3. HTML 转换为 Markdown 格式
4. 保存到本地目录

## 支持的网站

| 网站 | 状态 | 备注 |
|------|------|------|
| 微信公众号 | ✅ 已支持 | mp.weixin.qq.com |
| 知乎 | ✅ 已支持 | zhihu.com |
| CSDN | ✅ 已支持 | blog.csdn.net |
| 掘金 | ✅ 已支持 | juejin.cn |
| 其他网站 | ⚡ 部分支持 | 可能需要调整正则表达式 |

## 项目结构

```
article-saver/
├── README.md        # 本文件
├── SKILL.md         # Skill 配置文件
└── article-saver.py # 主程序脚本
```

## License

MIT License
