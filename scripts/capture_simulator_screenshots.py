#!/usr/bin/env python3
"""Small simctl wrapper for localized iOS simulator screenshots."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


LOCALES = {
    "zh-Hans": "zh_CN",
    "zh-Hant": "zh_TW",
    "en": "en_US",
    "ja": "ja_JP",
    "ko": "ko_KR",
    "fr": "fr_FR",
    "de": "de_DE",
    "es": "es_ES",
}


def run(cmd: list[str], check: bool = True) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=check)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", required=True, help="Simulator UDID")
    parser.add_argument("--bundle-id", required=True, help="App bundle id")
    parser.add_argument("--output", default="AppStoreAssets/raw", help="Output raw screenshot directory")
    parser.add_argument("--languages", default="en", help="Comma-separated Apple language codes")
    parser.add_argument("--app-path", help="Optional .app path to install first")
    parser.add_argument("--wait", type=float, default=4.0, help="Seconds to wait after launch")
    parser.add_argument("--name", default="01_recording.png", help="Screenshot filename inside each language folder")
    parser.add_argument("--grant", default="", help="Comma-separated privacy services, e.g. location-always,photos")
    parser.add_argument("--status-bar", action="store_true", help="Override status bar for stable screenshots")
    parser.add_argument("--boot", action="store_true", help="Boot and wait for the simulator first")
    args = parser.parse_args()

    if args.boot:
        run(["xcrun", "simctl", "boot", args.device], check=False)
        run(["xcrun", "simctl", "bootstatus", args.device, "-b"])

    if args.app_path:
        run(["xcrun", "simctl", "install", args.device, args.app_path])

    for service in [s.strip() for s in args.grant.split(",") if s.strip()]:
        run(["xcrun", "simctl", "privacy", args.device, "grant", service, args.bundle_id], check=False)

    if args.status_bar:
        run(
            [
                "xcrun",
                "simctl",
                "status_bar",
                args.device,
                "override",
                "--time",
                "09:41",
                "--wifiBars",
                "3",
                "--cellularBars",
                "4",
                "--batteryState",
                "charged",
                "--batteryLevel",
                "100",
            ],
            check=False,
        )

    out_root = Path(args.output)
    for language in [l.strip() for l in args.languages.split(",") if l.strip()]:
        locale = LOCALES.get(language, language)
        target_dir = out_root / language
        target_dir.mkdir(parents=True, exist_ok=True)
        run(["xcrun", "simctl", "terminate", args.device, args.bundle_id], check=False)
        run(
            [
                "xcrun",
                "simctl",
                "launch",
                args.device,
                args.bundle_id,
                "--args",
                "-AppleLanguages",
                f"({language})",
                "-AppleLocale",
                locale,
            ]
        )
        time.sleep(args.wait)
        run(["xcrun", "simctl", "io", args.device, "screenshot", str(target_dir / args.name)])


if __name__ == "__main__":
    main()
