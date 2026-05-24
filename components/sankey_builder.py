"""
sankey_builder.py
Core component for constructing the Plotly Sankey figure object.
Fully dynamic, supports any number of levels.
"""

import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
import numpy as np

from utils.color_utils import (
    generate_node_colors,
    generate_link_colors,
    PALETTES,
    hex_to_rgba,
)
from utils.hover_utils import build_node_hover, build_link_hover, build_node_labels


def build_sankey_figure(
    sankey_data: Dict,
    # --- Position ---
    node_x: Optional[List[float]] = None,
    node_y: Optional[List[float]] = None,
    # --- Colors ---
    palette_name: str = "Nature",
    node_color_by: str = "node",
    link_color_mode: str = "source",
    node_opacity: float = 0.9,
    link_opacity: float = 0.45,
    fixed_link_color: str = "#999999",
    manual_node_colors: Optional[Dict[str, str]] = None,
    bg_color: str = "#FFFFFF",
    paper_bg: str = "#FFFFFF",
    # --- Node style ---
    node_thickness: int = 20,
    node_pad: int = 15,
    node_line_color: str = "#333333",
    node_line_width: float = 0.8,
    # --- Label ---
    label_format: str = "name_value",
    metric_name: str = "Valor",
    metric_abbr: str = "n",
    decimal_places: int = 0,
    show_pct_hover: bool = True,
    show_rank_hover: bool = False,
    # --- Layout ---
    title: str = "Diagrama de Sankey",
    width: int = 1100,
    height: int = 650,
    margin_l: int = 20,
    margin_r: int = 20,
    margin_t: int = 60,
    margin_b: int = 20,
    # --- Font ---
    font_family: str = "Arial",
    font_size: int = 12,
    font_color: str = "#1A1A1A",
    title_font_size: int = 17,
    # --- Arrangement ---
    arrangement: str = "snap",   # "snap", "fixed", "perpendicular", "freeform"
    orientation: str = "h",      # "h" or "v"
) -> go.Figure:
    """
    Build and return a fully configured Plotly Sankey figure.
    """
    node_labels  = sankey_data["node_labels"]
    display_labels = sankey_data["display_labels"]
    sources      = sankey_data["sources"]
    targets      = sankey_data["targets"]
    values       = sankey_data["values"]
    node_totals  = sankey_data["node_totals"]
    node_level   = sankey_data["node_level"]
    level_cols   = sankey_data["level_cols"]
    grand_total  = sankey_data["grand_total"]

    # ── Node colors ─────────────────────────────────────────────────────────
    node_colors = generate_node_colors(
        node_labels=node_labels,
        node_level=node_level,
        palette_name=palette_name,
        node_opacity=node_opacity,
        color_by=node_color_by,
        manual_colors=manual_node_colors,
    )

    # ── Link colors ──────────────────────────────────────────────────────────
    link_colors = generate_link_colors(
        sources=sources,
        targets=targets,
        node_colors=node_colors,
        link_opacity=link_opacity,
        color_mode=link_color_mode,
        fixed_color=fixed_link_color,
    )

    # ── Hover texts ──────────────────────────────────────────────────────────
    node_hover = build_node_hover(
        node_labels=node_labels,
        display_labels=display_labels,
        node_totals=node_totals,
        grand_total=grand_total,
        node_level=node_level,
        level_cols=level_cols,
        metric_name=metric_name,
        decimal_places=decimal_places,
        show_pct=show_pct_hover,
        show_rank=show_rank_hover,
    )

    link_hover = build_link_hover(
        sources=sources,
        targets=targets,
        values=values,
        display_labels=display_labels,
        node_totals=node_totals,
        node_labels=node_labels,
        grand_total=grand_total,
        metric_name=metric_name,
        decimal_places=decimal_places,
    )

    # ── Node display labels ──────────────────────────────────────────────────
    formatted_labels = build_node_labels(
        display_labels=display_labels,
        node_totals=node_totals,
        node_labels=node_labels,
        label_format=label_format,
        grand_total=grand_total,
        decimal_places=decimal_places,
        metric_abbr=metric_abbr,
    )

    # ── Positions ────────────────────────────────────────────────────────────
    use_fixed = node_x is not None and node_y is not None
    actual_arrangement = "fixed" if use_fixed else arrangement

    # ── Build trace ──────────────────────────────────────────────────────────
    node_dict = dict(
        label=formatted_labels,
        color=node_colors,
        customdata=node_hover,
        hovertemplate="%{customdata}<extra></extra>",
        thickness=node_thickness,
        pad=node_pad,
        line=dict(color=node_line_color, width=node_line_width),
    )
    if use_fixed:
        node_dict["x"] = node_x
        node_dict["y"] = node_y

    sankey_trace = go.Sankey(
        arrangement=actual_arrangement,
        orientation=orientation,
        node=node_dict,
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            customdata=link_hover,
            hovertemplate="%{customdata}<extra></extra>",
        ),
        textfont=dict(
            family=font_family,
            size=font_size,
            color=font_color,
        ),
    )

    # ── Level annotations (column headers) ───────────────────────────────────
    annotations = _build_level_annotations(
        level_cols=level_cols,
        n_levels=len(level_cols),
        font_family=font_family,
        font_size=font_size - 1,
        font_color=font_color,
        bg_color=bg_color,
        node_x=node_x,
        node_labels=node_labels,
        node_level=node_level,
    )

    # ── Layout ───────────────────────────────────────────────────────────────
    layout = go.Layout(
        title=dict(
            text=title,
            font=dict(family=font_family, size=title_font_size, color=font_color),
            x=0.5,
            xanchor="center",
        ),
        width=width,
        height=height,
        paper_bgcolor=paper_bg,
        plot_bgcolor=bg_color,
        margin=dict(l=margin_l, r=margin_r, t=margin_t, b=margin_b),
        font=dict(family=font_family, size=font_size, color=font_color),
        hoverlabel=dict(
            bgcolor=bg_color,
            font_size=font_size,
            font_family=font_family,
            bordercolor=node_line_color,
        ),
        annotations=annotations,
    )

    fig = go.Figure(data=[sankey_trace], layout=layout)
    return fig


def _build_level_annotations(
    level_cols: List[str],
    n_levels: int,
    font_family: str,
    font_size: int,
    font_color: str,
    bg_color: str,
    node_x: Optional[List[float]],
    node_labels: List[str],
    node_level: Dict[str, int],
) -> List[dict]:
    """Generate column-header annotations above each level."""
    annotations = []
    x_step = 0.9 / max(n_levels - 1, 1)

    for i, col in enumerate(level_cols):
        # Determine x position
        if node_x is not None:
            # Average x of nodes at this level
            xs = [node_x[j] for j, lbl in enumerate(node_labels) if node_level.get(lbl, -1) == i]
            x_pos = np.mean(xs) if xs else (0.05 + i * x_step)
        else:
            x_pos = 0.05 + i * x_step

        annotations.append(dict(
            x=x_pos,
            y=1.04,
            xref="paper",
            yref="paper",
            text=f"<b>{col}</b>",
            showarrow=False,
            font=dict(family=font_family, size=font_size + 1, color=font_color),
            align="center",
        ))

    return annotations
