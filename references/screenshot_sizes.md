# Screenshot Sizes

Use this reference when choosing and validating App Store screenshots.

## Common Accepted Sizes

Recent iPhone portrait sizes commonly accepted by App Store Connect include:

- `1242 x 2688`
- `1284 x 2778`

Recent iPad portrait sizes commonly accepted by App Store Connect include:

- `2048 x 2732`
- `2064 x 2752`

App Store Connect may also accept landscape variants of those dimensions.

## Rules

- Always validate exact PNG dimensions after generation.
- Use a real simulator/device screenshot as the app UI layer.
- If App Store Connect reports a size error, use one of the exact accepted dimensions from the error message.
- If the app supports iPad, prepare iPad screenshots unless the app is made iPhone-only.
- Multi-language sets must use the matching localized app UI.

## Useful Validation

```bash
python3 - <<'PY'
from pathlib import Path
from PIL import Image
for path in Path("AppStoreAssets/screenshots").glob("**/*.png"):
    with Image.open(path) as img:
        print(path, img.size)
PY
```
