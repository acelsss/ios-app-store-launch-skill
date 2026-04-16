#!/usr/bin/env python3
"""Generate a multilingual App Store Connect metadata Markdown draft from JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SAMPLE_CONFIG = {
    "output": "AppStoreAssets/app_store_metadata.md",
    "app": {
        "canonical_name": "Example App",
        "copyright": "© 2026 Developer",
        "primary_category": "Utilities",
        "secondary_category": "Productivity",
        "support_urls": {"en": "https://example.com/apps/example/support/en/"},
        "privacy_urls": {"en": "https://example.com/apps/example/privacy/en/"},
    },
    "languages": {
        "en": {
            "label": "English",
            "name": "Example App",
            "subtitle": "A focused utility",
            "promotional_text": "A concise launch message.",
            "keywords": "utility,example,productivity",
            "description": "Long App Store description.",
            "release_notes": "Initial release.",
            "review_notes": "No account is required.",
        }
    },
    "privacy_answers": {
        "Does the app collect data from this app?": "Confirm against final binary.",
        "Tracking": "No, if no tracking SDK or cross-app tracking is present.",
    },
    "open_items": ["Confirm final privacy answers before submission."],
}


def table(rows: list[tuple[str, str]]) -> str:
    lines = ["| Language | Text |", "| --- | --- |"]
    for left, right in rows:
        escaped_right = right.replace("|", "\\|")
        lines.append(f"| {left} | {escaped_right} |")
    return "\n".join(lines)


def localized_rows(config: dict, key: str) -> list[tuple[str, str]]:
    rows = []
    for lang, data in config["languages"].items():
        rows.append((data.get("label", lang), str(data.get(key, ""))))
    return rows


def optional_url_rows(config: dict, key: str) -> list[str]:
    urls = config.get("app", {}).get(key, {})
    lines = []
    if isinstance(urls, dict):
        for lang, url in urls.items():
            lines.append(f"| {key.removesuffix('s').replace('_', ' ').title()} ({lang}) | {url} |")
    elif urls:
        lines.append(f"| {key.replace('_', ' ').title()} | {urls} |")
    return lines


def generate(config: dict[str, Any]) -> str:
    app = config.get("app", {})
    lines: list[str] = [
        "# App Store Connect Metadata Draft",
        "",
        "Use this file as a copy-and-paste checklist for App Store Connect localizations.",
        "",
        "## Shared Information",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Canonical app name | {app.get('canonical_name', '')} |",
        f"| Primary category | {app.get('primary_category', '')} |",
        f"| Secondary category | {app.get('secondary_category', '')} |",
        f"| Copyright | {app.get('copyright', '')} |",
    ]
    lines.extend(optional_url_rows(config, "support_urls"))
    lines.extend(optional_url_rows(config, "privacy_urls"))
    lines.extend(
        [
            "",
            "## App Name",
            "",
            table(localized_rows(config, "name")),
            "",
            "## Subtitle",
            "",
            table(localized_rows(config, "subtitle")),
            "",
            "## Promotional Text",
            "",
            table(localized_rows(config, "promotional_text")),
            "",
            "## Keywords",
            "",
            table(localized_rows(config, "keywords")),
            "",
            "## Description",
            "",
        ]
    )
    for lang, data in config["languages"].items():
        lines.extend([f"### {data.get('label', lang)}", "", str(data.get("description", "")), ""])
    lines.extend(["## Version Release Notes", "", table(localized_rows(config, "release_notes")), "", "## App Review Notes", ""])
    for lang, data in config["languages"].items():
        lines.extend([f"### {data.get('label', lang)}", "", str(data.get("review_notes", "")), ""])
    privacy = config.get("privacy_answers", {})
    if privacy:
        lines.extend(["## App Privacy Answers", "", "| Question | Suggested Answer |", "| --- | --- |"])
        for question, answer in privacy.items():
            escaped_answer = str(answer).replace("|", "\\|")
            lines.append(f"| {question} | {escaped_answer} |")
        lines.append("")
    open_items = config.get("open_items", [])
    if open_items:
        lines.extend(["## Open Items To Confirm", ""])
        for item in open_items:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Metadata JSON config")
    parser.add_argument("--output", help="Override output markdown path")
    parser.add_argument("--write-sample-config", help="Write a sample config and exit")
    args = parser.parse_args()

    if args.write_sample_config:
        Path(args.write_sample_config).write_text(json.dumps(SAMPLE_CONFIG, ensure_ascii=False, indent=2) + "\n")
        return
    if not args.config:
        raise SystemExit("Provide --config or --write-sample-config")
    config = json.loads(Path(args.config).read_text())
    output = Path(args.output or config.get("output", "AppStoreAssets/app_store_metadata.md"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate(config))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
