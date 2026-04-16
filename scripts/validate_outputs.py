#!/usr/bin/env python3
"""Validate generated App Store launch assets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


DEFAULT_ACCEPTED = {
    "iphone": {(1242, 2688), (2688, 1242), (1284, 2778), (2778, 1284)},
    "ipad": {(2064, 2752), (2752, 2064), (2048, 2732), (2732, 2048)},
}


def check_images(root: Path) -> tuple[int, int]:
    passed = 0
    failed = 0
    for path in sorted((root / "screenshots").glob("**/*.png")):
        if "overview" in path.name:
            continue
        with Image.open(path) as img:
            size = img.size
        family = "ipad" if "ipad" in path.parts else "iphone"
        if size in DEFAULT_ACCEPTED[family]:
            print(f"PASS image {path} {size}")
            passed += 1
        else:
            print(f"FAIL image {path} {size} not in accepted {family} sizes")
            failed += 1
    return passed, failed


def check_required_files(root: Path) -> tuple[int, int]:
    passed = 0
    failed = 0
    checks = [
        root / "app_store_metadata.md",
        root / "privacy_pages",
        root / "support_pages",
    ]
    for path in checks:
        if path.exists():
            print(f"PASS exists {path}")
            passed += 1
        else:
            print(f"WARN missing {path}")
    return passed, failed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="AppStoreAssets", help="Launch asset root")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings/failures")
    args = parser.parse_args()
    root = Path(args.root)

    passed_images, failed_images = check_images(root)
    passed_files, failed_files = check_required_files(root)
    total_failed = failed_images + failed_files
    print(f"Summary: {passed_images + passed_files} pass, {total_failed} fail")
    if total_failed or (args.strict and passed_images == 0):
        sys.exit(1)


if __name__ == "__main__":
    main()
