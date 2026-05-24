"""
dataframe_parser.py
Handles automatic detection of levels, column selection, and
conversion of any tabular DataFrame into Sankey-compatible structures.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
import io


def load_dataframe(uploaded_file) -> Optional[pd.DataFrame]:
    """Load CSV or Excel file into a DataFrame with error handling."""
    try:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            # Try multiple encodings
            for enc in ["utf-8", "latin-1", "cp1252"]:
                try:
                    df = pd.read_csv(uploaded_file, encoding=enc)
                    uploaded_file.seek(0)
                    return df
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    continue
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
            return df
    except Exception as e:
        raise ValueError(f"Erro ao carregar arquivo: {e}")
    return None


def detect_categorical_columns(df: pd.DataFrame, max_unique_ratio: float = 0.5) -> List[str]:
    """
    Auto-detect columns that are likely categorical (nodes).
    Uses dtype + unique ratio heuristic.
    """
    categorical = []
    for col in df.columns:
        if df[col].dtype == object or str(df[col].dtype) == "category":
            categorical.append(col)
        elif df[col].nunique() / max(len(df), 1) <= max_unique_ratio and df[col].nunique() <= 100:
            categorical.append(col)
    return categorical


def detect_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Auto-detect numeric columns suitable as value/weight."""
    return [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]


def build_sankey_data(
    df: pd.DataFrame,
    level_cols: List[str],
    value_col: str,
    aggregation: str = "sum",
    sort_by: str = "value",
    sort_ascending: bool = False,
    filter_zero: bool = True,
) -> Dict:
    """
    Convert a DataFrame with arbitrary level columns into Sankey source/target/value structure.

    Returns a dict with:
        - node_labels: list of unique node labels
        - node_indices: mapping label -> index
        - sources: list of source indices
        - targets: list of target indices
        - values: list of flow values
        - link_labels: list of hover labels per link
        - node_totals: dict of node -> total value
        - node_level: dict of node -> level index
        - level_nodes: dict of level_index -> list of nodes in order
    """
    if not level_cols or value_col not in df.columns:
        raise ValueError("Colunas inválidas fornecidas.")

    # Aggregate by all level columns
    agg_func = {"sum": "sum", "mean": "mean", "count": "count", "max": "max", "min": "min"}.get(aggregation, "sum")

    grouped = df.groupby(level_cols, observed=True)[value_col].agg(agg_func).reset_index()
    grouped.columns = list(level_cols) + ["_value"]

    if filter_zero:
        grouped = grouped[grouped["_value"] > 0]

    # Build node universe with level tracking
    node_level = {}   # node_label -> level index (0-based)
    level_nodes = {}  # level_idx -> ordered list of nodes

    for i, col in enumerate(level_cols):
        unique_vals = grouped[col].dropna().unique().tolist()
        # Sort nodes
        if sort_by == "value":
            node_vals = grouped.groupby(col, observed=True)["_value"].sum()
            unique_vals = node_vals.sort_values(ascending=sort_ascending).index.tolist()
        elif sort_by == "alpha":
            unique_vals = sorted(unique_vals, reverse=not sort_ascending)

        for v in unique_vals:
            label = f"{col}::{v}"  # namespace to avoid collision across levels
            if label not in node_level:
                node_level[label] = i
        level_nodes[i] = [f"{col}::{v}" for v in unique_vals]

    # Global node list (preserves level order)
    all_nodes = []
    for i in range(len(level_cols)):
        all_nodes.extend(level_nodes[i])

    node_indices = {n: idx for idx, n in enumerate(all_nodes)}

    # Build links between consecutive levels
    sources, targets, values, link_labels = [], [], [], []
    grand_total = grouped["_value"].sum()

    for pair_idx in range(len(level_cols) - 1):
        src_col = level_cols[pair_idx]
        tgt_col = level_cols[pair_idx + 1]

        pair_agg = grouped.groupby([src_col, tgt_col], observed=True)["_value"].agg(agg_func).reset_index()

        # Compute source totals for relative %
        src_totals = pair_agg.groupby(src_col, observed=True)["_value"].sum().to_dict()

        for _, row in pair_agg.iterrows():
            src_label = f"{src_col}::{row[src_col]}"
            tgt_label = f"{tgt_col}::{row[tgt_col]}"
            val = row["_value"]

            src_total = src_totals.get(row[src_col], 1)
            pct_total = (val / grand_total * 100) if grand_total > 0 else 0
            pct_src = (val / src_total * 100) if src_total > 0 else 0

            sources.append(node_indices[src_label])
            targets.append(node_indices[tgt_label])
            values.append(float(val))
            link_labels.append(
                f"<b>{row[src_col]}</b> → <b>{row[tgt_col]}</b><br>"
                f"Valor: {val:,.2f}<br>"
                f"% do total: {pct_total:.1f}%<br>"
                f"% de {row[src_col]}: {pct_src:.1f}%"
            )

    # Node totals (sum of all outgoing or incoming)
    node_totals = {}
    for label in all_nodes:
        col_name, val_name = label.split("::", 1)
        total = grouped[grouped[col_name].astype(str) == str(val_name)]["_value"].sum()
        node_totals[label] = float(total)

    # Display labels (strip namespace)
    display_labels = [lbl.split("::", 1)[1] for lbl in all_nodes]

    return {
        "node_labels": all_nodes,
        "display_labels": display_labels,
        "node_indices": node_indices,
        "sources": sources,
        "targets": targets,
        "values": values,
        "link_labels": link_labels,
        "node_totals": node_totals,
        "node_level": node_level,
        "level_nodes": level_nodes,
        "level_cols": level_cols,
        "grand_total": float(grand_total),
        "n_levels": len(level_cols),
    }


def compute_auto_positions(sankey_data: Dict) -> Tuple[List[float], List[float]]:
    """
    Generate smart default X/Y positions for nodes.
    X = evenly spaced by level, Y = evenly spaced within level.
    """
    level_cols = sankey_data["level_cols"]
    level_nodes = sankey_data["level_nodes"]
    node_labels = sankey_data["node_labels"]
    n_levels = sankey_data["n_levels"]

    node_x_map = {}
    node_y_map = {}

    x_step = 0.9 / max(n_levels - 1, 1)

    for lvl_idx, nodes in level_nodes.items():
        x = 0.05 + lvl_idx * x_step
        n = len(nodes)
        for j, node in enumerate(nodes):
            node_x_map[node] = x
            # Space from 0.05 to 0.95
            y = 0.05 + j * (0.90 / max(n - 1, 1)) if n > 1 else 0.5
            node_y_map[node] = round(max(0.001, min(0.999, y)), 4)

    x_list = [node_x_map.get(n, 0.5) for n in node_labels]
    y_list = [node_y_map.get(n, 0.5) for n in node_labels]

    return x_list, y_list


def get_sample_dataframe() -> pd.DataFrame:
    """Return a rich sample DataFrame for demonstration."""
    np.random.seed(42)
    regioes = ["Tapajós", "Araguaia", "Amazonas", "Xingu"]
    dietas = ["Herbívoro", "Carnívoro", "Onívoro", "Detritívoro"]
    especies = ["Sp. A", "Sp. B", "Sp. C", "Sp. D", "Sp. E"]
    sexos = ["Macho", "Fêmea"]
    estacoes = ["Chuva", "Seca"]

    rows = []
    for regiao in regioes:
        for dieta in np.random.choice(dietas, size=np.random.randint(2, 4), replace=False):
            for especie in np.random.choice(especies, size=np.random.randint(2, 4), replace=False):
                for sexo in sexos:
                    for estacao in estacoes:
                        val = np.random.randint(5, 200)
                        rows.append({
                            "Bacia": regiao,
                            "Grupo Trófico": dieta,
                            "Espécie": especie,
                            "Sexo": sexo,
                            "Estação": estacao,
                            "Abundância": val,
                            "Biomassa (g)": round(val * np.random.uniform(10, 50), 2),
                            "CPUE": round(val / np.random.uniform(1, 10), 3),
                        })
    return pd.DataFrame(rows)
