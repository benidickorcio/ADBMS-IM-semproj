# Color Palette Customization Guide

## Overview
Your application now uses a centralized color palette system. All colors are managed in a single file: `utils/colors.py`

This means you can change colors throughout the entire application by modifying values in just one place!

## Location
File: `utils/colors.py`

## Current Color Palette

### Primary Colors
```python
"primary": "#37E9FD"          # Cyan - Main accent color
"primary_dark": "#0B8A9D"     # Dark cyan
"primary_light": "#5FF5FF"    # Light cyan
```

### Secondary Colors
```python
"secondary": "#FFEE07"        # Yellow - Section labels
"secondary_dark": "#DAC600"   # Dark yellow
"secondary_light": "#FFFF4D"  # Light yellow
```

### Background Colors
```python
"bg_dark": "#1a1a1a"          # Dark background
"bg_darker": "#0f0f0f"        # Darker background
"bg_light": "#2a2a2a"         # Light background
```

### Button Colors
```python
"button_primary": "#2563eb"   # Blue - Main action buttons
"button_primary_dark": "#1d4ed8"  # Dark blue
"button_secondary": "#212222" # Dark gray - Secondary buttons
"button_secondary_dark": "#6b7280"  # Medium gray
"button_hover": "#1C565F"     # Hover state
"button_hover_secondary": "#4b5563"  # Secondary hover state
```

### Text Colors
```python
"text_primary": "#F4F4F4"     # Light text
"text_secondary": "#94a3b8"   # Secondary text
"text_dark": "#0B0B0B"        # Dark text
```

### Status Colors
```python
"status_success": "#34d399"   # Green
"status_error": "#f87171"     # Red/Light red
"status_error_dark": "#dc2626" # Dark red
"status_warning": "#fbbf24"   # Amber
```

### Utility Colors
```python
"border": "#404040"           # Border color
"divider": "#333333"          # Divider color
"accent_add": "#25b6c9"       # Add/positive action
"accent_delete": "#dc2626"    # Delete/negative action
```

## How to Customize

### Example 1: Change Primary Color (Header)
1. Open `utils/colors.py`
2. Find: `"primary": "#37E9FD"`
3. Replace with your desired hex color, e.g.: `"primary": "#FF6B6B"`
4. Save the file
5. Restart the application - the header and all primary elements will update!

### Example 2: Change Button Colors
1. Open `utils/colors.py`
2. Find the Button Colors section
3. Modify as needed:
   - `"button_primary"` - Main action buttons (blue)
   - `"button_secondary"` - Alternative buttons (gray)
4. Save and restart

### Example 3: Change Success/Error Status Colors
1. Open `utils/colors.py`
2. Find the Status Colors section
3. Modify:
   - `"status_success"` - For success messages
   - `"status_error"` - For error messages
   - `"status_warning"` - For warnings
4. Save and restart

## Applied Screens

The color palette is now applied to:
- ✅ Login Screen (login.py)
- ✅ Main Application (app.py)
- ✅ Point of Sales/POS (pos.py)
- ✅ Customers Management (customers_ui.py)
- ✅ Inventory Management (inventory.py)
- ✅ Sales Reports (sales.py)
- ✅ Settings (settings.py)
- ❌ Dashboard (excluded per request)

## Tips for Color Selection

### Recommended Color Combinations

**Modern Blue Theme:**
```python
"primary": "#0066CC"
"button_primary": "#0066CC"
"status_success": "#00AA00"
```

**Corporate Green Theme:**
```python
"primary": "#00A86B"
"button_primary": "#00A86B"
"secondary": "#FF8C00"
```

**Dark Purple Theme:**
```python
"primary": "#7C3AED"
"button_primary": "#7C3AED"
"secondary": "#FBBF24"
```

### Color Picker Resources
- Use online hex color pickers: https://www.color-hex.com/
- Test contrast for readability: https://webaim.org/resources/contrastchecker/

## Hex Color Format

All colors use **hexadecimal (hex) format**: `#RRGGBB`
- `#` = Hex indicator
- `RR` = Red value (00-FF)
- `GG` = Green value (00-FF)
- `BB` = Blue value (00-FF)

Example: `#FF0000` = Red, `#00FF00` = Green, `#0000FF` = Blue

## How Colors Are Used in Code

The palette is imported in each view file:
```python
from utils.colors import get_color

# Usage in code:
text_color=get_color("primary")
fg_color=get_color("button_primary")
```

The `get_color()` function retrieves colors from the palette dictionary.

## Need to Add New Colors?

You can add new colors to `utils/colors.py`:
```python
COLOR_PALETTE = {
    # ... existing colors ...
    "my_custom_color": "#ABCDEF",  # Add your color here
}
```

Then use it anywhere:
```python
custom_fg=get_color("my_custom_color")
```

---

**Happy Customizing!** 🎨

For any questions or issues, refer back to this guide or check the `utils/colors.py` file directly.
