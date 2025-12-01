# Icons & Assets

This directory contains open-source compatible SVG icons used throughout the Virtual Electrical Designer application.

## Icon Locations

All icons are stored in the `assets/icons/` directory as `.svg` files.

## Available Icons

- `library.svg` - Component library icon
- `properties.svg` - Properties inspector icon
- `analysis.svg` - Analysis/output icon
- `console.svg` - Console/terminal icon
- `waveforms.svg` - Waveforms/graph icon
- `reports.svg` - Reports/document icon

## Using Icons in Code

### Method 1: Using IconLoader (Recommended)

```python
from frontend.utils.icon_loader import get_icon, get_pixmap

# Get as QIcon (for use in UI elements)
icon = get_icon('library', size=24)
button.setIcon(icon)

# Get as QPixmap (for direct drawing)
pixmap = get_pixmap('reports', size=32)
```

### Method 2: Direct File Path

```python
from pathlib import Path
from PySide6.QtGui import QIcon

icon_path = Path(__file__).parent.parent.parent / "assets/icons/library.svg"
icon = QIcon(str(icon_path))
```

## Icon Guidelines

- All icons are in SVG format for scalability
- Icons should be simple, clean, and recognizable
- Use `stroke="currentColor"` in SVG for color support
- Icons work best at 16px, 24px, 32px, and 48px sizes
- All icons are open-source compatible (CC0 or similar licenses)

## Adding New Icons

1. Create a new `.svg` file in `assets/icons/`
2. Use a consistent style with existing icons
3. Use `stroke="currentColor"` and `stroke-width="2"` for consistency
4. Test with `IconLoader.get_icon('icon_name')` in your code

## Icon Sources

These icons are based on open-source icon designs from:
- Lucide Icons (MIT License)
- Feather Icons (MIT License)
- Custom designs following open-source icon standards

All icons are completely free to use and modify for this project.
