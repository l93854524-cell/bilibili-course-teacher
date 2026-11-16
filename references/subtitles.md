# 字幕获取

## 识别课程

- 支持 BV 号、B 站公开视频链接、b23.tv 短链。先把短链展开成 B 站链接，保留最终链接的 `p` 参数。
- 从视频页面或 B 站的 `/x/web-interface/view?bvid=BV...` 读取 `pages` 和分 P 时长。对合集或系列页面，读取当前课程的条目列表，记录每一项的 BV 与 P，先取当前要教的课次。若只打开了合集中的一个视频，用户说「整套」时检查关联的合集范围。无法读取课程列表时，从可确认的章节先教，必要时说明已覆盖的范围。
- 未指定范围的单视频链接，用它指向的视频；单 BV 下有多 P 且没给 `p` 时，学习范围包含可识别的所有 P，从首课开始随进度取字幕。用户明确限定一节或几节时按限定处理。
- 用户提供 SRT、VTT、带时间戳 JSON 或 TXT 时，保留原始文件。纯文本没有时间戳时按段落或行号标记。

## 使用随包附带的提取工具

本包附带 [bilibili-ai-subtitle](https://github.com/ccBilly-aipm/bilibili-ai-subtitle) 的 MIT 许可提取器，也内置了已实测的 macOS Chrome 多配置入口。使用环境需要 Python 3.10+、联网，并可读取用户本地浏览器的 B 站登录态。用 Agent 的常规方式在隔离环境安装一次依赖。从本 Skill 的 `scripts` 目录运行，输出路径使用实际绝对路径。

**macOS 上已在 Chrome 登录 B 站时，优先用下面的入口。** 它会检查默认配置和其他 Chrome 配置，导出中文字幕的 TXT、SRT，并报告字幕条数、首尾时间和片尾缺口。

```sh
python -m pip install -r requirements.txt
python extract_chrome.py BV... --page 1 --output-dir "/absolute/course-dir/captions" --name BV...-p1
```

**其他系统或浏览器，使用上游入口。** 自动模式会尝试受支持的浏览器，也可指定用户已登录的浏览器。macOS Chrome 入口找不到登录状态但其他浏览器已登录时，也可以用这个入口。

```sh
python -m pip install -r requirements.txt
python -m bilibili_ai_subtitle BV... --browser auto --page 1 --format json --output "/absolute/course-dir/captions/BV...-p1.json"
```

上游 CLI 需要显式指定 `--page`，所以先解析链接参数；短链先展开再传 BV。用 `--list` 可检查 AI 轨道。提取后检查实际返回的语言，命令默认优先中文 AI 字幕，也可能返回其他 AI 轨道。提取器只处理 AI 字幕。播放器可见人工字幕、或者用户持有字幕文件时，可按实际可用能力导入。提取器来源为 ccBilly-aipm/bilibili-ai-subtitle，版本 0.1.0，修订 2898964d19d7923908b4dc1f9c2623d50f79ce9f，许可随代码保留。

遇到站点限流时遵守服务端返回的重试时间，避免短时间反复请求。

## 检查结果与继续方式

逐节确认字幕有内容、时间起止有效、语种适合任务。视频前后出现明显缺口时在覆盖表标明，字幕尾点接近片尾也只说明覆盖到那个时间。课程缺字幕、需登录、页面无法访问、Agent 在云端读不到本地浏览器时，给出实际卡点，优先请用户提供字幕文件或用已拿到的课继续。仅当用户明确要转写且环境支持时，才调用音频转写流程，并注明转写来源。浏览器登录由用户在本地完成，生成的老师文件和分享包里只放课程内容与出处。
