"""
color_utils.py
Palettes, gradients, template colors, and node/link color generation.
"""

import colorsys
import random
from typing import List, Dict, Optional, Tuple
import numpy as np


# ── Scientific / publication-ready palettes ─────────────────────────────────

PALETTES = {
    "Nature": [
        "#4E79A7", "#F28E2B", "#E15759", "#76B7B2",
        "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7",
        "#9C755F", "#BAB0AC",
    ],
    "Science": [
        "#003366", "#006699", "#0099CC", "#33BBEE",
        "#CC3311", "#EE7733", "#FFBB33", "#009988",
        "#AA3377", "#BBBBBB",
    ],
    "Pastel": [
        "#AEC6CF", "#FFD1DC", "#B5EAD7", "#FFDAC1",
        "#C7CEEA", "#F8B4D9", "#FAD7A0", "#A3E4D7",
        "#D7BDE2", "#A9CCE3",
    ],
    "Dark": [
        "#1F77B4", "#FF7F0E", "#2CA02C", "#D62728",
        "#9467BD", "#8C564B", "#E377C2", "#7F7F7F",
        "#BCBD22", "#17BECF",
    ],
    "High Contrast": [
        "#000000", "#E69F00", "#56B4E9", "#009E73",
        "#F0E442", "#0072B2", "#D55E00", "#CC79A7",
        "#999999", "#FFFFFF",
    ],
    "Minimal": [
        "#2D2D2D", "#555555", "#888888", "#AAAAAA",
        "#CCCCCC", "#4A90D9", "#50C878", "#FF6B6B",
        "#FFA500", "#9B59B6",
    ],
    "Publication": [
        "#264653", "#2A9D8F", "#E9C46A", "#F4A261",
        "#E76F51", "#457B9D", "#A8DADC", "#1D3557",
        "#6D6875", "#B5838D",
    ],
    "Viridis": [
        "#440154", "#482878", "#3E4989", "#31688E",
        "#26828E", "#1F9E89", "#35B779", "#6DCD59",
        "#B4DE2C", "#FDE725",
    ],
    "Plasma": [
        "#0D0887", "#46039F", "#7201A8", "#9C179E",
        "#BD3786", "#D8576B", "#ED7953", "#FB9F3A",
        "#FDCF2A", "#F0F921",
    ],
    "Ecological": [
        "#1A5276", "#1F618D", "#2874A6", "#2E86C1",
        "#3498DB", "#27AE60", "#229954", "#1E8449",
        "#196F3D", "#145A32",
    ],
}

TEMPLATES = {
    "publication": {
        "bg_color": "#FFFFFF",
        "paper_bg": "#FFFFFF",
        "font_color": "#1A1A1A",
        "font_family": "Times New Roman",
        "font_size": 13,
        "title_font_size": 18,
        "palette": "Publication",
        "node_opacity": 1.0,
        "link_opacity": 0.45,
        "node_thickness": 20,
        "node_pad": 16,
        "node_line_color": "#333333",
        "node_line_width": 0.8,
    },
    "minimal": {
        "bg_color": "#FAFAFA",
        "paper_bg": "#FAFAFA",
        "font_color": "#333333",
        "font_family": "Helvetica Neue",
        "font_size": 12,
        "title_font_size": 16,
        "palette": "Minimal",
        "node_opacity": 0.9,
        "link_opacity": 0.35,
        "node_thickness": 16,
        "node_pad": 12,
        "node_line_color": "#CCCCCC",
        "node_line_width": 0.5,
    },
    "dark": {
        "bg_color": "#1A1A2E",
        "paper_bg": "#16213E",
        "font_color": "#E0E0E0",
        "font_family": "Courier New",
        "font_size": 12,
        "title_font_size": 17,
        "palette": "Dark",
        "node_opacity": 0.95,
        "link_opacity": 0.4,
        "node_thickness": 22,
        "node_pad": 14,
        "node_line_color": "#444466",
        "node_line_width": 1.0,
    },
    "nature": {
        "bg_color": "#F5F5F0",
        "paper_bg": "#F5F5F0",
        "font_color": "#2C3E50",
        "font_family": "Georgia",
        "font_size": 13,
        "title_font_size": 18,
        "palette": "Nature",
        "node_opacity": 0.9,
        "link_opacity": 0.5,
        "node_thickness": 20,
        "node_pad": 15,
        "node_line_color": "#7F8C8D",
        "node_line_width": 0.8,
    },
    "scientific": {
        "bg_color": "#FFFFFF",
        "paper_bg": "#FFFFFF",
        "font_color": "#003366",
        "font_family": "Arial",
        "font_size": 12,
        "title_font_size": 16,
        "palette": "Science",
        "node_opacity": 1.0,
        "link_opacity": 0.5,
        "node_thickness": 18,
        "node_pad": 12,
        "node_line_color": "#003366",
        "node_line_width": 1.0,
    },
    "pastel": {
        "bg_color": "#FEFEFE",
        "paper_bg": "#FEFEFE",
        "font_color": "#555555",
        "font_family": "Verdana",
        "font_size": 12,
        "title_font_size": 15,
        "palette": "Pastel",
        "node_opacity": 0.85,
        "link_opacity": 0.55,
        "node_thickness": 18,
        "node_pad": 14,
        "node_line_color": "#AAAAAA",
        "node_line_width": 0.5,
    },
    "high_contrast": {
        "bg_color": "#FFFFFF",
        "paper_bg": "#FFFFFF",
        "font_color": "#000000",
        "font_family": "Arial Black",
        "font_size": 13,
        "title_font_size": 18,
        "palette": "High Contrast",
        "node_opacity": 1.0,
        "link_opacity": 0.6,
        "node_thickness": 24,
        "node_pad": 16,
        "node_line_color": "#000000",
        "node_line_width": 1.5,
    },
}


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert hex color string to rgba() string."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha:.3f})"


def generate_node_colors(
    node_labels: List[str],
    node_level: Dict[str, int],
    palette_name: str = "Nature",
    node_opacity: float = 0.9,
    color_by: str = "level",         # "level", "node", "manual"
    manual_colors: Optional[Dict[str, str]] = None,
) -> List[str]:
    """
    Generate RGBA color strings for each node.
    color_by:
        'level'  - all nodes in the same level share a base hue
        'node'   - each unique node name gets a distinct color
        'manual' - use manual_colors dict (label -> hex)
    """
    palette = PALETTES.get(palette_name, PALETTES["Nature"])
    colors = []

    for label in node_labels:
        if color_by == "manual" and manual_colors and label in manual_colors:
            colors.append(hex_to_rgba(manual_colors[label], node_opacity))
        elif color_by == "level":
            lvl = node_level.get(label, 0)
            base = palette[lvl % len(palette)]
            colors.append(hex_to_rgba(base, node_opacity))
        else:
            # Hash the node name to a palette index for consistency
            idx = abs(hash(label)) % len(palette)
            colors.append(hex_to_rgba(palette[idx], node_opacity))

    return colors


def generate_link_colors(
    sources: List[int],
    targets: List[int],
    node_colors: List[str],
    link_opacity: float = 0.4,
    color_mode: str = "source",  # "source", "target", "gradient", "fixed"
    fixed_color: str = "#999999",
) -> List[str]:
    """
    Generate RGBA color strings for each link.
    """
    link_colors = []
    for src, tgt in zip(sources, targets):
        if color_mode == "source":
            base = node_colors[src]
        elif color_mode == "target":
            base = node_colors[tgt]
        elif color_mode == "fixed":
            base = hex_to_rgba(fixed_color, link_opacity)
            link_colors.append(base)
            continue
        else:
            base = node_colors[src]

        # Reapply desired opacity
        if base.startswith("rgba("):
            parts = base[5:-1].split(",")
            r, g, b = parts[0], parts[1], parts[2]
            link_colors.append(f"rgba({r},{g},{b},{link_opacity:.3f})")
        else:
            link_colors.append(hex_to_rgba(fixed_color, link_opacity))

    return link_colors
