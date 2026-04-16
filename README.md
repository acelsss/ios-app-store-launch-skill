# iOS App Store Launch Skill

A Codex skill for preparing iOS apps for App Store Connect submission.

It helps an agent create real-UI App Store screenshots, localized iPhone and iPad image sets, App Store Connect metadata drafts, local privacy and support pages, pricing guidance, and a final validation checklist.

## What It Does

- Inspects an iOS project for Xcode files, localizations, app display names, permission strings, and privacy-relevant code patterns.
- Captures localized simulator screenshots through `xcrun simctl` when Xcode is available.
- Generates App Store-sized marketing screenshots using real app screenshots as the UI layer.
- Generates multilingual App Store Connect metadata in Markdown.
- Generates local static privacy policy and support pages for the developer to deploy.
- Validates generated screenshot dimensions and required launch files.

## Important Principle

The skill should not invent the in-app UI shown inside App Store screenshots.

Marketing copy, visual framing, and background treatment can be generated, but the app UI layer should come from real simulator or device screenshots unless the user explicitly approves placeholders.

## Installation

Copy this folder into your Codex skills directory:

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R ios-app-store-launch-skill "$CODEX_HOME/skills/ios-app-store-launch"
```

If `CODEX_HOME` is not set, the default is usually `~/.codex`:

```bash
mkdir -p ~/.codex/skills
cp -R ios-app-store-launch-skill ~/.codex/skills/ios-app-store-launch
```

Install Python dependencies when using the screenshot generator or validator:

```bash
python3 -m pip install -r requirements.txt
```

## Usage

In Codex, ask:

```text
Use $ios-app-store-launch to prepare this iOS app for App Store submission.
```

The skill will first inspect the project, then ask only for missing information such as target languages, iPhone/iPad support, core selling points, developer contact email, and whether Xcode simulators may be used.

## Script Examples

Discover project facts:

```bash
python scripts/discover_ios_app.py --root /path/to/ios/project --output discovery.json
```

Write a sample screenshot config:

```bash
python scripts/generate_app_store_screenshots.py --write-sample-config screenshot_config.json
```

Generate metadata from a JSON config:

```bash
python scripts/generate_metadata.py --write-sample-config metadata_config.json
python scripts/generate_metadata.py --config metadata_config.json
```

Generate local privacy and support pages:

```bash
python scripts/generate_web_pages.py --write-sample-config web_pages_config.json
python scripts/generate_web_pages.py --config web_pages_config.json
```

Validate launch assets:

```bash
python scripts/validate_outputs.py --root AppStoreAssets
```

## Requirements

- Python 3.10+
- Pillow for screenshot generation and image validation
- Xcode command line tools for simulator screenshot capture
- `ripgrep` is recommended for fast project searches

## Legal And Privacy Note

Generated privacy policies and App Privacy answers are draft assistance only. Review the final app binary, dependencies, network behavior, and App Store Connect requirements before submission.

## License

MIT
