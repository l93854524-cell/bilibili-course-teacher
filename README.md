# B 站课程快学

给支持 Agent Skills 的助手一条 B 站课程链接。拿到字幕后，助手会先介绍整节课的学习路线，再用课堂示范开讲。讲解顺序和节奏由课程内容及学习进展决定。

## 开始使用

1. 下载或克隆本仓库，把整个目录交给支持 `SKILL.md` 的 Agent 加载。
2. 启用 **B 站课程快学**，发一个 B 站课程链接。也可以直接提供 SRT、VTT、TXT 或带时间戳的 JSON。
3. 做完当前步骤后，Agent 会沿课程清单带入下一项。课程长时，可分几次继续学。

例如，发「用 B 站课程快学，带我学 https://www.bilibili.com/video/BV…/」。

自动提取需要 Agent 可以联网、运行 Python 3.10+，并读取已登录 B 站的本地浏览器。macOS Chrome 多配置提取工具已随包附带。提取失败时，可直接提供字幕文件。

## 文件

| 路径 | 内容 |
| --- | --- |
| [SKILL.md](SKILL.md) | 链接或字幕到开讲的入口，包含课程路线和带学规则 |
| [references/teacher.md](references/teacher.md) | 从字幕提取教法、核对逐项教学清单、生成练习和速记材料 |
| [references/subtitles.md](references/subtitles.md) | 视频、分 P 和合集的字幕获取及故障处理 |
| [scripts/](scripts/) | 随仓库提供的字幕提取器、依赖和上游许可证 |

## 当前状态

已用真实四级课程验证取字幕后开讲、答题和接续教学。最新版逐项核对流程仍待用整节真实课程从头到尾复测。遇到字幕缺失的关键公式、板书或图时，需要对应的课件或画面补充。

字幕提取复用 [ccBilly-aipm/bilibili-ai-subtitle](https://github.com/ccBilly-aipm/bilibili-ai-subtitle)，上游 [MIT 许可证](scripts/bilibili_ai_subtitle/LICENSE) 随代码保留。
