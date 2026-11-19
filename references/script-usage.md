# 本地脚本使用

依赖：Python 3.10 或以上。除图片工具外只使用Python标准库。先将工作目录切到本Skill文件夹，或把命令中的相对路径替换为实际绝对路径。下述输出文件/目录必须尚不存在；重试时使用新路径，原输入和旧结果都保留。

```sh
python scripts/check_sitemap.py references/sitemap.xml --host example.com --output sitemap-result.json
```

## 输入与示例预期

输入XML或.gz；--host只填精确主机名，不含协议/路径。可选--crawl crawl.csv，表头url,status,final_url,canonical，填写实际抓取记录而非推测。示例应发现重复和越域，网络状态未知。

## 能力边界

sitemapindex只核对索引，子XML须分别提供并处理。标准支持参考：https://www.sitemaps.org/protocol.html 。离线检查不能证明收录或当前HTTP可达性。

所有样例使用example.com及虚构资料，不能当客户实测。脚本不含遥测或付费API，不会发布内容。发现问题会写入报告，不代表执行异常；命令参数或输入格式错误返回退出码2。图片工具有文件处理失败时返回1并保留manifest；跳过动画会记录原因。
