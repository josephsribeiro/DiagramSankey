"""
hover_utils.py
Build rich, scientific hover text for Sankey nodes and links.
"""

from typing import List, Dict, Optional


def build_node_hover(
    node_labels: List[str],
    display_labels: List[str],
    node_totals: Dict[str, float],
    grand_total: float,
    node_level: Dict[str, int],
    level_cols: List[str],
    metric_name: str = "Valor",
    decimal_places: int = 2,
    show_pct: bool = True,
    show_rank: bool = False,
) -> List[str]:
    """
    Generate hover text for each node in the Sankey diagram.
    """
    hover_texts = []

    # Pre-compute rank within each level
    level_rank: Dict[str, int] = {}
    if show_rank:
        from collections import defaultdict
        level_groups: Dict[int, List] = defaultdict(list)
        for label in node_labels:
            lvl = node_level.get(label, 0)
            level_groups[lvl].append((label, node_totals.get(label, 0)))
        for lvl, items in level_groups.items():
            sorted_items = sorted(items, key=lambda x: -x[1])
            for rank, (lbl, _) in enumerate(sorted_items, 1):
                level_rank[lbl] = rank

    for label, display in zip(node_labels, display_labels):
        total = node_totals.get(label, 0)
        lvl = node_level.get(label, 0)
        col_name = level_cols[lvl] if lvl < len(level_cols) else "Nível"
        pct = (total / grand_total * 100) if grand_total > 0 else 0

        lines = [
            f"<b>{display}</b>",
            f"<i>Nível: {col_name}</i>",
            f"{metric_name}: <b>{total:,.{decimal_places}f}</b>",
        ]
        if show_pct:
            lines.append(f"% do total: <b>{pct:.1f}%</b>")
        if show_rank and label in level_rank:
            lines.append(f"Rank no nível: #{level_rank[label]}")

        hover_texts.append("<br>".join(lines))

    return hover_texts


def build_link_hover(
    sources: List[int],
    targets: List[int],
    values: List[float],
    display_labels: List[str],
    node_totals: Dict[str, float],
    node_labels: List[str],
    grand_total: float,
    metric_name: str = "Valor",
    decimal_places: int = 2,
) -> List[str]:
    """
    Generate hover text for each link in the Sankey diagram.
    """
    hover_texts = []
    label_map = {i: lbl.split("::", 1)[1] for i, lbl in enumerate(node_labels)}

    for src_idx, tgt_idx, val in zip(sources, targets, values):
        src_name = label_map.get(src_idx, "?")
        tgt_name = label_map.get(tgt_idx, "?")

        src_total = node_totals.get(node_labels[src_idx], 1)
        pct_total = (val / grand_total * 100) if grand_total > 0 else 0
        pct_src = (val / src_total * 100) if src_total > 0 else 0

        lines = [
            f"<b>{src_name} → {tgt_name}</b>",
            f"{metric_name}: <b>{val:,.{decimal_places}f}</b>",
            f"% do total: <b>{pct_total:.1f}%</b>",
            f"% de {src_name}: <b>{pct_src:.1f}%</b>",
        ]
        hover_texts.append("<br>".join(lines))

    return hover_texts


def build_node_labels(
    display_labels: List[str],
    node_totals: Dict[str, float],
    node_labels: List[str],
    label_format: str = "name_value",   # "name_only", "name_value", "name_n", "name_pct"
    grand_total: float = 1.0,
    decimal_places: int = 0,
    metric_abbr: str = "n",
) -> List[str]:
    """
    Format displayed node labels for the Sankey diagram.
    """
    labels = []
    for display, label in zip(display_labels, node_labels):
        total = node_totals.get(label, 0)
        pct = (total / grand_total * 100) if grand_total > 0 else 0

        if label_format == "name_only":
            labels.append(display)
        elif label_format == "name_value":
            val_str = f"{total:,.{decimal_places}f}" if decimal_places > 0 else f"{int(total):,}"
            labels.append(f"{display} ({val_str})")
        elif label_format == "name_n":
            val_str = f"{total:,.{decimal_places}f}" if decimal_places > 0 else f"{int(total):,}"
            labels.append(f"{display}<br>{metric_abbr} = {val_str}")
        elif label_format == "name_pct":
            labels.append(f"{display} ({pct:.1f}%)")
        else:
            labels.append(display)

    return labels
