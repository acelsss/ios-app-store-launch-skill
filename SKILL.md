---
name: ios-app-store-launch
description: Prepare an iOS app for App Store submission, including real-device or simulator-based screenshots, localized iPhone and iPad App Store images, App Store Connect metadata, local privacy policy pages, local support pages, pricing guidance, and a final submission checklist. Use when the user asks to prepare, package, localize, or review an iPhone/iPad app before submitting it to App Store Connect.
metadata:
  short-description: Prepare iOS App Store launch assets
---

# iOS App Store Launch

Use this skill to prepare an iOS app for App Store Connect: real UI screenshots, localized App Store images, metadata, local privacy/support pages, pricing notes, and a final checklist.

## Core Rules

- Never invent the in-app UI shown inside App Store screenshots. Capture real simulator/device UI unless the user explicitly accepts placeholders.
- Localized screenshot sets must use matching localized app UI captures.
- Generate privacy/support pages locally by default. Do not deploy pages, modify production websites, change App Store Connect settings, or submit for review as part of this skill.
- Treat privacy policy and App Privacy answers as draft guidance unless the final binary has been checked for analytics, ads, account systems, crash reporting SDKs, server uploads, or tracking.
- Validate generated image sizes and page files before final handoff.

## Workflow

1. **Discover**: Inspect the project before asking questions. Use `scripts/discover_ios_app.py` when useful.
2. **Ask only what is missing**: Confirm languages, device families, paid/free model, core promise, screenshot style, developer name/email, website plan, and permission to use Xcode/simulators.
3. **Plan screenshot themes**: Choose a flexible count based on selling points. A utility app often needs 4-7 screens, but do not force a fixed count.
4. **Capture real UI**: Use Xcode/simulator where available. `scripts/capture_simulator_screenshots.py` provides a reusable `simctl` wrapper.
5. **Generate screenshots**: Use `scripts/generate_app_store_screenshots.py` with a JSON config. Adapt copy, themes, raw screenshot paths, and dimensions.
6. **Generate metadata**: Use `scripts/generate_metadata.py` to create a structured Markdown draft.
7. **Generate local web pages**: Use `scripts/generate_web_pages.py` for local privacy/support HTML pages. Tell the user where to upload them.
8. **Validate**: Use `scripts/validate_outputs.py` to check image dimensions and required files.
9. **Handoff**: Provide generated paths, suggested URLs, validation summary, and remaining App Store Connect decisions.

## What To Inspect

Look for:

- Xcode project/workspace, schemes, bundle identifier, deployment target, and supported devices.
- `Info.plist`, localized `InfoPlist.strings`, `Localizable.strings`, string catalogs, and app display names.
- Existing screenshots, design files, icons, brand assets, and App Store materials.
- Privacy-relevant code or dependencies: analytics, ads, networking, account systems, crash reporting, location, photos, camera, contacts, health, purchases.

Useful commands:

```bash
python scripts/discover_ios_app.py --root .
xcodebuild -list
rg "Analytics|Firebase|Crash|Sentry|AdMob|tracking|URLSession|location|Photo|PHPhoto|StoreKit"
```

## Questions To Ask

Ask compactly and only for missing information:

1. Which App Store localizations are needed?
2. Is the app iPhone-only or iPhone + iPad?
3. Is it paid, free, subscription, or undecided?
4. What is the core promise in one sentence?
5. What screenshot style should be used?
6. What developer name and contact email should appear in support/privacy pages?
7. Is there an existing website for privacy/support pages, and where will the local generated pages be uploaded?
8. May the assistant use Xcode simulators/devices to capture real UI?

## Screenshot Planning

For each screenshot, define:

- Main headline.
- Supporting line.
- Real UI screen or crop needed.
- Optional visual metaphor outside the real UI.
- Localized copy per language.
- Target device family and dimensions.

Common utility-app theme menu:

- Core promise / pain point solved.
- Main action or setup flow.
- Privacy or local-data trust point.
- Batch or advanced workflow.
- Safety rules / error avoidance.
- Export, sharing, reporting, or power-user feature.
- Settings, customization, automation, or integration features when they improve conversion.

Get user confirmation before major visual generation if themes are uncertain.

## Screenshot Generation

Prefer the bundled generator:

```bash
python3 -m pip install -r requirements.txt
python scripts/generate_app_store_screenshots.py \
  --config AppStoreAssets/screenshot_config.json
```

Accepted dimension defaults:

- iPhone portrait: `1284 x 2778`, or another App Store Connect accepted size.
- iPad portrait: `2064 x 2752`, or another App Store Connect accepted size.

Rules:

- Use real raw screenshots as the phone/tablet UI layer.
- Keep marketing text and visual treatment outside the real UI.
- Create overview/contact-sheet images for review.
- Run size validation after generation.

## Metadata

Generate `AppStoreAssets/app_store_metadata.md`. Include:

- App name, subtitle, promotional text, keywords, description.
- What's New / version release notes.
- Categories, copyright, support URL, privacy URL.
- App Review notes.
- App Privacy guidance and age rating notes.
- Pricing recommendation and open items.

For short fields, use language tables. For long descriptions, use separate sections by language. Do not include exact paid prices in the app description.

## Local Privacy And Support Pages

Generate local static HTML pages when URLs are missing:

```bash
python scripts/generate_web_pages.py \
  --config AppStoreAssets/web_pages_config.json
```

Recommended URL structure:

```text
https://example.com/apps/{app-slug}/privacy/
https://example.com/apps/{app-slug}/privacy/zh-cn/
https://example.com/apps/{app-slug}/privacy/en/
https://example.com/apps/{app-slug}/privacy/ja/
https://example.com/apps/{app-slug}/support/
https://example.com/apps/{app-slug}/support/zh-cn/
https://example.com/apps/{app-slug}/support/en/
https://example.com/apps/{app-slug}/support/ja/
```

Do not deploy by SSH/Git/manual upload in the default flow. If the user later asks for deployment help, treat that as a separate task.

## Pricing Guidance

For focused utility apps, default advice:

- Start with one-time paid purchase.
- Consider a low-friction launch price near the local equivalent of USD 1.99.
- Use Apple's automatic price conversion first.
- Avoid manual country-specific pricing until there is conversion, refund, and review data.
- Remind the user that paid apps require Apple paid app agreements, tax, and banking setup.

## Validation

Run:

```bash
python scripts/validate_outputs.py \
  --root AppStoreAssets
```

Before final handoff, verify:

- iPhone screenshots exist for each localization and match accepted dimensions.
- iPad screenshots exist if required and match accepted dimensions.
- Screenshot UI language matches marketing language.
- Metadata Markdown exists and includes required fields.
- Local privacy/support page files exist.
- User-provided deployed URLs, if any, return 200.
- Privacy guidance remains draft unless the final binary was checked.

## References

Load only when needed:

- `references/app_store_fields.md` for metadata fields and copy constraints.
- `references/screenshot_sizes.md` for screenshot dimensions and validation.
- `references/privacy_policy_guidance.md` for privacy policy and App Privacy cautions.
- `references/pricing_guidance.md` for pricing strategy.

## Boundaries

- Do not submit to App Store Connect without explicit user instruction.
- Do not claim legal compliance. Say "draft privacy policy" or "submission guidance" unless reviewed by the user or counsel.
- Do not infer that the app collects no data if dependencies or network behavior suggest otherwise.
- Do not use fake screenshots of app UI. If real capture is blocked, stop and ask for screenshots.
- Do not store SSH passwords or private credentials in generated files.
