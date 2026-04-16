#!/usr/bin/env python3
"""Discover useful App Store launch facts from an iOS project."""

from __future__ import annotations

import argparse
import json
import plistlib
import re
import subprocess
from pathlib import Path


PRIVACY_PATTERNS = {
    "analytics": r"Analytics|FirebaseAnalytics|Amplitude|Mixpanel|Telemetry",
    "ads": r"AdMob|GAD|advertisingIdentifier|AppLovin|UnityAds",
    "crash_reporting": r"Sentry|Crashlytics|Bugsnag|PLCrashReporter",
    "networking": r"URLSession|Alamofire|Network\.framework|http://|https://",
    "location": r"CoreLocation|CLLocation|NSLocation",
    "photos": r"PhotoKit|PHPhoto|PhotosUI|NSPhotoLibrary",
    "tracking": r"ATTrackingManager|NSUserTrackingUsageDescription|trackingAuthorization",
    "purchases": r"StoreKit|Product\.products|SKPayment",
}


def run(cmd: list[str], cwd: Path) -> str:
    try:
        return subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def parse_strings(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    text = path.read_text(errors="ignore")
    for match in re.finditer(r'"([^"]+)"\s*=\s*"((?:\\"|[^"])*)"\s*;', text):
        data[match.group(1)] = match.group(2).replace('\\"', '"')
    return data


def read_plist(path: Path) -> dict:
    try:
        with path.open("rb") as f:
            return plistlib.load(f)
    except Exception:
        return {}


def find_project_files(root: Path) -> dict:
    return {
        "xcodeproj": [str(p.relative_to(root)) for p in root.rglob("*.xcodeproj") if "DerivedData" not in p.parts],
        "xcworkspace": [str(p.relative_to(root)) for p in root.rglob("*.xcworkspace") if "DerivedData" not in p.parts],
        "info_plist": [str(p.relative_to(root)) for p in root.rglob("Info.plist") if "DerivedData" not in p.parts],
        "localizable": [str(p.relative_to(root)) for p in root.rglob("Localizable.strings")],
        "info_plist_strings": [str(p.relative_to(root)) for p in root.rglob("InfoPlist.strings")],
    }


def detect_localizations(root: Path) -> list[str]:
    langs = set()
    for lproj in root.rglob("*.lproj"):
        if lproj.is_dir():
            langs.add(lproj.name.removesuffix(".lproj"))
    return sorted(langs)


def detect_info(root: Path, plist_paths: list[str]) -> dict:
    infos = []
    for rel in plist_paths:
        path = root / rel
        plist = read_plist(path)
        if not plist:
            continue
        infos.append(
            {
                "path": rel,
                "bundle_identifier": plist.get("CFBundleIdentifier"),
                "display_name": plist.get("CFBundleDisplayName") or plist.get("CFBundleName"),
                "version": plist.get("CFBundleShortVersionString"),
                "build": plist.get("CFBundleVersion"),
                "background_modes": plist.get("UIBackgroundModes", []),
                "supported_orientations": plist.get("UISupportedInterfaceOrientations", []),
                "supported_orientations_ipad": plist.get("UISupportedInterfaceOrientations~ipad", []),
                "permission_keys": {
                    k: v
                    for k, v in plist.items()
                    if k.startswith("NS") and ("UsageDescription" in k or "Tracking" in k)
                },
            }
        )
    return {"plist_files": infos}


def detect_localized_display_names(root: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for strings_path in root.rglob("InfoPlist.strings"):
        lang = strings_path.parent.name.removesuffix(".lproj")
        values = parse_strings(strings_path)
        if values:
            result[lang] = values
    return result


def scan_privacy_flags(root: Path) -> dict[str, bool]:
    files = []
    for ext in ("*.swift", "*.m", "*.mm", "*.plist", "*.strings", "*.json", "*.pbxproj"):
        files.extend(root.rglob(ext))
    content = "\n".join(
        p.read_text(errors="ignore")[:250_000]
        for p in files
        if "DerivedData" not in p.parts and ".git" not in p.parts
    )
    return {name: bool(re.search(pattern, content, re.IGNORECASE)) for name, pattern in PRIVACY_PATTERNS.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Project root to inspect")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = find_project_files(root)
    report = {
        "root": str(root),
        "files": files,
        "localizations": detect_localizations(root),
        "info": detect_info(root, files["info_plist"]),
        "localized_info_plist_strings": detect_localized_display_names(root),
        "privacy_flags": scan_privacy_flags(root),
        "xcodebuild_list": run(["xcodebuild", "-list"], root),
    }

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n")
    print(payload)


if __name__ == "__main__":
    main()
