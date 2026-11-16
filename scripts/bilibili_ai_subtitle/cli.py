"""Command-line interface designed for people and AI agents."""

import argparse
import json
import sys
from pathlib import Path

import httpx

from .extractor import BilibiliAIExtractor, SubtitleError, get_sessdata
from .formatter import default_output_path, render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="只抓取 B站 AI 字幕，不下载视频或音频。",
        epilog=(
            "Example: bilibili-ai-subtitle 'https://www.bilibili.com/video/BV...' "
            "--browser chrome --format srt"
        ),
    )
    parser.add_argument("source", help="B站视频 URL 或 BV 号")
    parser.add_argument(
        "--browser",
        choices=["chrome", "edge", "firefox", "brave", "auto"],
        default="chrome",
        help="读取 B站登录 Cookie 的浏览器（默认 chrome）",
    )
    parser.add_argument("--page", type=int, default=1, help="分P编号（默认 1）")
    parser.add_argument("--language", default="ai-zh", help="AI 字幕语言（默认 ai-zh）")
    parser.add_argument(
        "--format",
        choices=["srt", "txt", "json"],
        default="srt",
        help="输出格式（默认 srt）",
    )
    parser.add_argument("--output", "-o", help="输出路径；省略时保存到当前目录")
    parser.add_argument("--stdout", action="store_true", help="输出到 stdout，不写文件")
    parser.add_argument("--list", action="store_true", help="只列出 AI 字幕轨道")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        sessdata = get_sessdata(args.browser)
        with BilibiliAIExtractor(sessdata) as extractor:
            if args.list:
                info, tracks = extractor.list_ai_tracks(args.source, args.page)
                print(
                    json.dumps(
                        {
                            "bvid": info["bvid"],
                            "video_title": info["title"],
                            "tracks": [
                                {"lan": track.get("lan"), "lan_doc": track.get("lan_doc")}
                                for track in tracks
                            ],
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
                return

            result = extractor.extract(args.source, args.page, args.language)
        content = render(result, args.format)
        if args.stdout:
            print(content, end="")
            return

        output_path = Path(args.output).expanduser().resolve() if args.output else None
        output_path = output_path or default_output_path(result, args.format)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(
            json.dumps(
                {
                    "ok": True,
                    "output": str(output_path),
                    "subtitle_count": result["subtitle_count"],
                    "language": result["language"],
                    "video_title": result["video_title"],
                    "media_downloaded": False,
                },
                ensure_ascii=False,
            )
        )
    except (SubtitleError, httpx.HTTPError) as error:
        print(f"错误 / Error: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
