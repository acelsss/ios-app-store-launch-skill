# iOS App Store Launch Skill

一个用于准备 iOS App 上架 App Store Connect 素材的 Codex skill。

A Codex skill for preparing iOS apps for App Store Connect submission.

## 中文说明

这个 skill 可以帮助 Codex 准备 iOS App 上架前常见的材料：真实界面的 App Store 截图、多语言 iPhone/iPad 图片、App Store Connect 文案草稿、本地隐私政策页、本地技术支持页、定价建议和最终校验清单。

### 它能做什么

- 检查 iOS 项目中的 Xcode 文件、本地化语言、App 显示名称、权限文案和隐私相关代码特征。
- 在可使用 Xcode 的情况下，通过 `xcrun simctl` 捕获不同语言的模拟器真实截图。
- 基于真实 App 截图生成符合 App Store 尺寸要求的宣传图。
- 生成多语言 App Store Connect metadata Markdown 草稿。
- 生成本地静态隐私政策页和技术支持页，由开发者自行部署到网站。
- 校验生成的截图尺寸和必需的上架文件。

### 重要原则

这个 skill 不应该虚构 App Store 截图里的应用界面。

营销文案、外层视觉包装和背景可以生成，但截图里的 App UI 应该来自真实模拟器或真机截图，除非用户明确接受占位图。

### 安装

把这个目录复制到 Codex 的 skills 目录：

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R ios-app-store-launch-skill "$CODEX_HOME/skills/ios-app-store-launch"
```

如果没有设置 `CODEX_HOME`，通常可以使用默认目录 `~/.codex`：

```bash
mkdir -p ~/.codex/skills
cp -R ios-app-store-launch-skill ~/.codex/skills/ios-app-store-launch
```

使用截图生成或图片校验脚本前，安装 Python 依赖：

```bash
python3 -m pip install -r requirements.txt
```

### 使用方式

在 Codex 中可以这样说：

```text
使用 $ios-app-store-launch 帮我准备这个 iOS App 上架 App Store 的素材。
```

这个 skill 会先检查项目，然后只询问缺失的信息，例如目标语言、是否支持 iPad、核心卖点、开发者联系邮箱，以及是否可以使用 Xcode 模拟器截图。

### 脚本示例

检查项目基本信息：

```bash
python scripts/discover_ios_app.py --root /path/to/ios/project --output discovery.json
```

生成截图配置示例：

```bash
python scripts/generate_app_store_screenshots.py --write-sample-config screenshot_config.json
```

根据 JSON 配置生成 metadata：

```bash
python scripts/generate_metadata.py --write-sample-config metadata_config.json
python scripts/generate_metadata.py --config metadata_config.json
```

生成本地隐私政策页和技术支持页：

```bash
python scripts/generate_web_pages.py --write-sample-config web_pages_config.json
python scripts/generate_web_pages.py --config web_pages_config.json
```

校验上架素材：

```bash
python scripts/validate_outputs.py --root AppStoreAssets
```

### 运行要求

- Python 3.10+
- Pillow，用于截图生成和图片尺寸校验
- Xcode command line tools，用于模拟器截图捕获
- 推荐安装 `ripgrep`，用于快速搜索项目代码

### 法律和隐私说明

生成的隐私政策和 App Privacy 回答只是草稿辅助。提交前请检查最终 App 二进制文件、依赖库、网络行为和 App Store Connect 的实际要求。

## English

This skill helps Codex prepare common launch materials for an iOS app: real-UI App Store screenshots, localized iPhone/iPad image sets, App Store Connect metadata drafts, local privacy policy pages, local support pages, pricing guidance, and a final validation checklist.

### What It Does

- Inspects an iOS project for Xcode files, localizations, app display names, permission strings, and privacy-relevant code patterns.
- Captures localized simulator screenshots through `xcrun simctl` when Xcode is available.
- Generates App Store-sized marketing screenshots using real app screenshots as the UI layer.
- Generates multilingual App Store Connect metadata in Markdown.
- Generates local static privacy policy and support pages for the developer to deploy.
- Validates generated screenshot dimensions and required launch files.

### Important Principle

The skill should not invent the in-app UI shown inside App Store screenshots.

Marketing copy, visual framing, and background treatment can be generated, but the app UI layer should come from real simulator or device screenshots unless the user explicitly approves placeholders.

### Installation

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

### Usage

In Codex, ask:

```text
Use $ios-app-store-launch to prepare this iOS app for App Store submission.
```

The skill will first inspect the project, then ask only for missing information such as target languages, iPhone/iPad support, core selling points, developer contact email, and whether Xcode simulators may be used.

### Script Examples

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

### Requirements

- Python 3.10+
- Pillow for screenshot generation and image validation
- Xcode command line tools for simulator screenshot capture
- `ripgrep` is recommended for fast project searches

### Legal And Privacy Note

Generated privacy policies and App Privacy answers are draft assistance only. Review the final app binary, dependencies, network behavior, and App Store Connect requirements before submission.

## License

MIT
