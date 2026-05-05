
COLOR_PALETTE = {
    # Background Colors
    "bg_primary": "#111827",       # Dark primary background (main)
    "bg_secondary": "#1f2937",     # Card/Panel background
    "bg_tertiary": "#162032",      # Alternative card background
    "bg_light": "#374151",         # Light background/borders
    
    # Primary Accent Colors
    "primary": "#22d3ee",          # Cyan - Main accent color
    "primary_dark": "#0891b2",     # Dark cyan
    "primary_light": "#67e8f9",    # Light cyan
    
    # Secondary Accent Colors
    "secondary": "#a78bfa",        # Purple - Section labels
    "secondary_dark": "#7c3aed",   # Dark purple
    "secondary_light": "#c4b5fd",  # Light purple
    
    # Additional Accents
    "accent_pink": "#f472b6",      # Pink accent
    "accent_blue": "#60a5fa",      # Blue accent
    
    # Text Colors
    "text_primary": "#f9fafb",     # Light text
    "text_secondary": "#6b7280",   # Secondary text
    "text_dark": "#0B0B0B",        # Dark text
    
    # Button Colors
    "button_primary": "#60a5fa",   # Blue buttons
    "button_primary_dark": "#3b82f6",  # Dark blue
    "button_secondary": "#1f2937", # Dark gray - Secondary buttons
    "button_secondary_dark": "#374151",  # Medium gray
    "button_hover": "#22d3ee",     # Cyan hover
    "button_hover_secondary": "#4b5563",  # Secondary hover state
    
    # Status Colors
    "status_success": "#34d399",   # Green
    "status_success_dark": "#10b981",  # Dark green
    "status_error": "#f87171",     # Red/Light red
    "status_error_dark": "#dc2626", # Dark red
    "status_warning": "#fbbf24",   # Amber
    "status_warning_dark": "#d97706",  # Dark amber
    
    # Utility Colors
    "border": "#374151",           # Border color
    "divider": "#1f2937",          # Divider color
    "accent_add": "#22d3ee",       # Add/positive action
    "accent_delete": "#f87171",    # Delete/negative action
}

# Function to get color value
def get_color(color_name: str, default: str = "#f9fafb") -> str:
    return COLOR_PALETTE.get(color_name, default)
