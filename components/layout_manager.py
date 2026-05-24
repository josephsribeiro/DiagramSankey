"""
layout_manager.py
Manages node positions: auto-generation, manual override via UI,
and intelligent redistribution.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import streamlit as st


def auto_layout(
    sankey_data: Dict,
    x_margin: float = 0.05,
    y_margin: float = 0.05,
    value_weighted_y: bool = False,
) -> Tuple[List[float], List[float]]:
    """
    Compute automatic X/Y positions for all nodes.
    Optionally weight vertical position by node value.
    """
    level_nodes = sankey_data["level_nodes"]
    node_labels = sankey_data["node_labels"]
    node_totals = sankey_data["node_totals"]
    n_levels = sankey_data["n_levels"]

    node_x_map: Dict[str, float] = {}
    node_y_map: Dict[str, float] = {}

    x_step = (1.0 - 2 * x_margin) / max(n_levels - 1, 1)

    for lvl_idx, nodes in level_nodes.items():
        x = x_margin + lvl_idx * x_step
        n = len(nodes)

        if value_weighted_y and n > 1:
            vals = np.array([node_totals.get(nd, 0) for nd in nodes], dtype=float)
            total = vals.sum()
            if total > 0:
                cumulative = np.cumsum(vals) / total
                # Center each node around its cumulative midpoint
                prev = np.concatenate([[0], cumulative[:-1]])
                centers = (prev + cumulative) / 2
                # Scale to [y_margin, 1 - y_margin]
                centers = y_margin + centers * (1 - 2 * y_margin)
                for nd, cy in zip(nodes, centers):
                    node_x_map[nd] = round(x, 4)
                    node_y_map[nd] = round(np.clip(cy, 0.001, 0.999), 4)
                continue

        for j, nd in enumerate(nodes):
            node_x_map[nd] = round(x, 4)
            y = y_margin + j * (1.0 - 2 * y_margin) / max(n - 1, 1) if n > 1 else 0.5
            node_y_map[nd] = round(np.clip(y, 0.001, 0.999), 4)

    x_list = [node_x_map.get(nd, 0.5) for nd in node_labels]
    y_list = [node_y_map.get(nd, 0.5) for nd in node_labels]
    return x_list, y_list


def render_position_editor(
    sankey_data: Dict,
    default_x: List[float],
    default_y: List[float],
) -> Tuple[List[float], List[float]]:
    """
    Render Streamlit widgets that let the user manually adjust
    X and Y positions of each node.
    Returns updated x_list, y_list.
    """
    node_labels = sankey_data["node_labels"]
    display_labels = sankey_data["display_labels"]
    level_nodes = sankey_data["level_nodes"]
    level_cols = sankey_data["level_cols"]
    n_levels = sankey_data["n_levels"]

    st.markdown("#### 📐 Posicionamento Manual dos Nós")
    st.caption("Ajuste a posição X (horizontal) e Y (vertical) de cada nó individualmente.")

    # Initialize session state
    if "node_positions" not in st.session_state:
        st.session_state["node_positions"] = {
            nd: {"x": round(default_x[i], 3), "y": round(default_y[i], 3)}
            for i, nd in enumerate(node_labels)
        }

    updated_x = list(default_x)
    updated_y = list(default_y)

    node_index = {nd: i for i, nd in enumerate(node_labels)}

    for lvl_idx in range(n_levels):
        nodes_at_lvl = level_nodes.get(lvl_idx, [])
        col_name = level_cols[lvl_idx]

        with st.expander(f"Nível {lvl_idx + 1}: {col_name} ({len(nodes_at_lvl)} nós)", expanded=False):
            # X is shared per level — offer a global X slider + per-node Y
            first_nd = nodes_at_lvl[0] if nodes_at_lvl else None
            if first_nd:
                current_x = st.session_state["node_positions"].get(first_nd, {}).get("x", default_x[node_index[first_nd]])
                level_x = st.slider(
                    f"X do Nível '{col_name}'",
                    min_value=0.0, max_value=1.0,
                    value=float(current_x),
                    step=0.01,
                    key=f"level_x_{lvl_idx}",
                )
                # Apply X to all nodes at this level
                for nd in nodes_at_lvl:
                    st.session_state["node_positions"].setdefault(nd, {})["x"] = level_x

            for nd in nodes_at_lvl:
                idx = node_index[nd]
                display = display_labels[idx]
                cur_y = st.session_state["node_positions"].get(nd, {}).get("y", default_y[idx])
                new_y = st.slider(
                    f"Y de '{display}'",
                    min_value=0.001, max_value=0.999,
                    value=float(cur_y),
                    step=0.01,
                    key=f"node_y_{nd}",
                )
                st.session_state["node_positions"][nd]["y"] = new_y

    # Rebuild lists in node order
    for i, nd in enumerate(node_labels):
        pos = st.session_state["node_positions"].get(nd, {})
        updated_x[i] = pos.get("x", default_x[i])
        updated_y[i] = pos.get("y", default_y[i])

    if st.button("🔄 Restaurar Posições Automáticas", key="reset_positions"):
        st.session_state["node_positions"] = {
            nd: {"x": round(default_x[i], 3), "y": round(default_y[i], 3)}
            for i, nd in enumerate(node_labels)
        }
        st.rerun()

    return updated_x, updated_y
