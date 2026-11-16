"""Export Bilibili AI subtitles using an existing local Chrome login."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import browser_cookie3
import httpx
from bilibili_ai_subtitle.extractor import BilibiliAIExtractor, NoAISubtitleError
from bilibili_ai_subtitle.formatter import render


def resolve_source(source: str) -> str:
    if re.fullmatch(r"BV[a-zA-Z0-9]+", source, re.IGNORECASE):
        return source
    parsed = urlparse(source)
    if parsed.scheme != "https" or parsed.hostname not in {"b23.tv", "www.bilibili.com", "bilibili.com"}:
        raise ValueError("Expected a Bilibili HTTPS video or b23.tv link, or a BV id")
    if parsed.hostname == "b23.tv":
        with httpx.Client(follow_redirects=True, timeout=20) as client:
            response = client.get(source)
            source = str(response.url)
    parsed = urlparse(source)
    if parsed.hostname not in {"www.bilibili.com", "bilibili.com"}:
        raise ValueError("Short link did not resolve to bilibili.com")
    if not re.search(r"/video/BV[a-zA-Z0-9]+", parsed.path, re.IGNORECASE):
        raise ValueError("Link does not contain a BV video id")
    return source


def chrome_sessdata() -> tuple[str, str]:
    chrome = Path.home() / "Library/Application Support/Google/Chrome"
    profiles = [chrome / "Default", *sorted(chrome.glob("Profile *"))]
    for profile in profiles:
        cookies = profile / "Cookies"
        if not cookies.is_file():
            continue
        try:
            jar = browser_cookie3.chrome(cookie_file=str(cookies), domain_name=".bilibili.com")
            session = next((cookie.value for cookie in jar if cookie.name == "SESSDATA" and cookie.value), None)
            if session:
                return session, profile.name
        except Exception:
            continue
    raise RuntimeError("No Bilibili login found in Chrome profiles. Log in to Bilibili in Chrome and retry.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Bilibili video URL, b23.tv URL, or BV id")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd())
    parser.add_argument("--name", help="Output filename stem; defaults to the BV id")
    parser.add_argument("--page", type=int, help="Video part; defaults to the link's p parameter or 1")
    args = parser.parse_args()

    try:
        source = resolve_source(args.source)
        page = args.page if args.page is not None else int(
            parse_qs(urlparse(source).query).get("p", ["1"])[0]
        )
        if page < 1:
            raise ValueError("Video part must be a positive integer")
        session, profile = chrome_sessdata()
        with BilibiliAIExtractor(session) as extractor:
            info = extractor.get_video_info(source, page)
            result = extractor.extract(source, page)
        if result["language"] != "ai-zh":
            raise NoAISubtitleError("The selected track is not ai-zh")
    except httpx.HTTPStatusError as error:
        message = f"Bilibili request failed (HTTP {error.response.status_code})"
        retry_after = error.response.headers.get("Retry-After")
        if retry_after:
            message += f"; retry after {retry_after}"
        parser.exit(2, f"{message}\n")
    except httpx.RequestError:
        parser.exit(2, "Network error while requesting Bilibili subtitles\n")
    except (RuntimeError, ValueError) as error:
        parser.exit(2, f"{error}\n")
    cues = result["subtitles"]
    if not cues or any(cue["to"] < cue["from"] for cue in cues):
        raise ValueError("Subtitle cues are empty or have invalid time ranges")
    stem = args.name or info["bvid"] + (f"_p{page}" if page != 1 else "")
    if not re.fullmatch(r"[\w-]+", stem):
        raise ValueError("--name must contain only letters, numbers, underscores, or hyphens")
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for format_name in ("txt", "srt"):
        path = output_dir / f"{stem}.{format_name}"
        path.write_text(render(result, format_name), encoding="utf-8")
        files[format_name] = str(path)
    print(json.dumps({
        "bvid": info["bvid"], "title": info["title"], "page": page,
        "chrome_profile": profile, "language": result["language"],
        "subtitle_count": len(cues), "duration_seconds": info["duration"],
        "first_cue_seconds": cues[0]["from"], "last_cue_seconds": cues[-1]["to"],
        "tail_gap_seconds": round(info["duration"] - cues[-1]["to"], 3),
        "files": files,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
