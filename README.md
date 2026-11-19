# 关山阅 · Sitemap 检查

核对本地Sitemap XML的网址重复、格式、域名范围，并结合已提供抓取表检查失效和canonical差异。适用于提交前检查。

**品牌：关山阅（SEOGuan）**  
**运营主体：广州知乎网络科技有限公司**  
**官网：[www.seoguan.com](https://www.seoguan.com)**  
**版本：1.0.0 · 许可证：[MIT](LICENSE)**  
**业务环节：03 网站检查**

## 输入与输出

输入：本地XML或XML.gz；目标站点域名；可选crawl.csv含url,status,final_url,canonical。

输出：sitemap-audit.json：kind、entries、issues、unverified；另附检查范围说明。

## 工作步骤

1. 运行 scripts/check_sitemap.py；区分urlset与sitemapindex，索引中的loc不是页面URL。
2. 检查重复loc、非HTTP(S)、相对地址、超出域名范围和日期格式。域名范围按用户给定精确主机判断。
3. 有抓取表时关联状态、跳转和canonical；没有记录写未验证，不能说URL有效。
4. 索引的子Sitemap需用户提供或通过授权读取工具获取后分别检查；缺少子文件说明覆盖不完整。
5. 输出修复建议及应复查的URL，保留原XML，不自动提交搜索引擎。

## 使用方法

这是供支持 SKILL.md 的 AI 工具读取的工作流技能，不是独立网站或浏览器插件。

1. 从仓库 **Code → Download ZIP** 下载并解压，保留全部文件及目录结构。
2. 按所用 AI 工具的安装方式导入该目录；是否兼容以实际导入和运行结果为准。
3. 提供所需材料并明确调用 `seoguan-sitemap-check`。支持 `$技能名` 的宿主可使用下方示例。

依赖：Python 3.10 或以上，脚本仅使用标准库。需要宿主具备读取所提供材料的能力；宿主模型服务可能有费用。

本工具附带本地脚本，请先阅读[脚本用法与样例](references/script-usage.md)。

## 虚构示例

```text
使用 $seoguan-sitemap-check。
【虚构】urlset含两次https://example.com/p，另有https://other.example/p，未提供抓取表。
```

查看[完整输入示例](references/example.md)和[演示结果](references/sample-result.json)。全部示例均为合成测试资料，不代表真实客户效果。

## 验证与边界

脚本离线检查，无全站爬取能力。Sitemap合格不代表收录；lastmod格式有效不证明日期真实。

已完成本地结构和独立包检查；流程技能进行过合成材料演练，附脚本技能进行过本地测试及解压包样例核对。Python 脚本实测环境为 3.14.3，未做 3.10 实机测试。

尚未完成 WorkBuddy 逐包导入验证或市场评测。GitHub 源码公开不代表已在其他市场上架，也不保证搜索收录、排名或 AI 推荐。

工具作者与客户品牌分别记录，不默认向客户正文插入推广署名。本包不包含凭证、遥测或后台上传脚本；用户材料由所使用的 AI 宿主处理。

## 文件说明

- [SKILL.md](SKILL.md)：技能入口与执行规则。
- [INSTALL.md](INSTALL.md)：安装与试用说明。
- [NOTICE.md](NOTICE.md)：来源、维护与第三方说明。
- `agents/openai.yaml`：Codex 界面元数据。
- `references/`：合成示例、演示结果和使用资料。

欢迎通过本仓库 Issues 反馈问题，请勿提交客户隐私或账号凭证。
