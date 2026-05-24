"""
app.py  ─  SankeyPro: Advanced Dynamic Sankey Generator
Streamlit + Plotly Graph Objects

Run:
    streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np

# ── Internal modules ─────────────────────────────────────────────────────────
from utils.dataframe_parser import (
    load_dataframe,
    detect_categorical_columns,
    detect_numeric_columns,
    build_sankey_data,
    get_sample_dataframe,
)
from components.sankey_builder import build_sankey_figure
from components.layout_manager import auto_layout, render_position_editor
from components.style_manager import build_full_config
from components.export_manager import render_export_panel

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SankeyPro — Gerador Avançado de Sankey",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global resets ── */
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f1724 0%, #1a2744 60%, #0f2035 100%);
    color: #e0e6f0;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stMultiSelect label {
    color: #c8d8ee !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #7ec8e3 !important;
}
section[data-testid="stSidebar"] .stDivider { opacity: 0.3; }

/* ── Header banner ── */
.sankey-header {
    background: linear-gradient(135deg, #0f1724 0%, #1a3a5c 50%, #0e2438 100%);
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid #2a4a6a;
}
.sankey-header h1 {
    color: #7ec8e3;
    margin: 0;
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.sankey-header p {
    color: #93b4cc;
    margin: 6px 0 0;
    font-size: 1.0rem;
}

/* ── Metric cards ── */
.metric-row { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.metric-card {
    background: linear-gradient(135deg, #1a3a5c, #0f2035);
    border: 1px solid #2a4a6a;
    border-radius: 10px;
    padding: 14px 20px;
    flex: 1;
    min-width: 140px;
    text-align: center;
}
.metric-card .value { color: #7ec8e3; font-size: 1.6rem; font-weight: 700; }
.metric-card .label { color: #7a9ab8; font-size: 0.78rem; margin-top: 2px; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f0f4f8;
    border-radius: 8px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #1a3a5c !important;
    color: white !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1a3a5c, #0e5a8a);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0e5a8a, #1a3a5c);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(14,90,138,0.3);
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #2d6a4f, #1b4332);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

/* ── Info boxes ── */
.stInfo { border-left-color: #7ec8e3 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "df": None,
        "sankey_data": None,
        "fig": None,
        "use_sample": False,
        "manual_positions": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — DATA SOURCE
# ═══════════════════════════════════════════════════════════════════════════════
def sidebar_data_section() -> pd.DataFrame | None:
    st.sidebar.markdown("## 📂 Fonte de Dados")

    use_sample = st.sidebar.button("🧪 Usar Dataset de Exemplo", use_container_width=True)
    if use_sample:
        st.session_state["df"] = get_sample_dataframe()
        st.session_state["use_sample"] = True
        # Clear positions when data changes
        if "node_positions" in st.session_state:
            del st.session_state["node_positions"]

    uploaded = st.sidebar.file_uploader(
        "Ou carregue seu arquivo (CSV / Excel)",
        type=["csv", "xlsx", "xls"],
        key="file_uploader",
    )
    if uploaded:
        try:
            df = load_dataframe(uploaded)
            if df is not None:
                st.session_state["df"] = df
                st.session_state["use_sample"] = False
                if "node_positions" in st.session_state:
                    del st.session_state["node_positions"]
        except ValueError as e:
            st.sidebar.error(str(e))

    return st.session_state.get("df")


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — COLUMN SELECTION
# ═══════════════════════════════════════════════════════════════════════════════
def sidebar_column_selection(df: pd.DataFrame):
    st.sidebar.divider()
    st.sidebar.markdown("## 🏗️ Estrutura do Sankey")

    cat_cols = detect_categorical_columns(df)
    num_cols = detect_numeric_columns(df)

    if not cat_cols:
        st.sidebar.error("Nenhuma coluna categórica detectada.")
        st.stop()
    if not num_cols:
        st.sidebar.error("Nenhuma coluna numérica detectada.")
        st.stop()

    level_cols = st.sidebar.multiselect(
        "Colunas de Nível (ordem = fluxo do Sankey)",
        options=cat_cols,
        default=cat_cols[:min(4, len(cat_cols))],
        key="level_cols",
    )

    if len(level_cols) < 2:
        st.sidebar.warning("Selecione pelo menos 2 colunas de nível.")
        st.stop()

    value_col = st.sidebar.selectbox(
        "Coluna de Valores",
        options=num_cols,
        key="value_col",
    )

    st.sidebar.divider()
    st.sidebar.markdown("## ⚙️ Processamento")

    aggregation = st.sidebar.selectbox(
        "Agregação",
        ["sum", "mean", "count", "max", "min"],
        format_func=lambda x: {"sum": "Soma", "mean": "Média", "count": "Contagem",
                                "max": "Máximo", "min": "Mínimo"}[x],
        key="aggregation",
    )

    sort_by = st.sidebar.selectbox(
        "Ordenar nós por",
        ["value", "alpha", "none"],
        format_func=lambda x: {"value": "📊 Valor", "alpha": "🔤 Alfabético", "none": "— Nenhum"}[x],
        key="sort_by",
    )
    sort_asc = st.sidebar.checkbox("Ordem crescente", False, key="sort_ascending")
    filter_zero = st.sidebar.checkbox("Remover fluxos zero/negativos", True, key="filter_zero")

    # ── Filters ─────────────────────────────────────────────────────────────
    st.sidebar.divider()
    st.sidebar.markdown("## 🔍 Filtros")
    filters = {}
    with st.sidebar.expander("Filtrar categorias", expanded=False):
        for col in level_cols:
            uniq = sorted(df[col].dropna().unique().tolist(), key=str)
            sel = st.multiselect(f"{col}", uniq, default=uniq, key=f"filter_{col}")
            if sel != uniq:
                filters[col] = sel

    return level_cols, value_col, aggregation, sort_by, sort_asc, filter_zero, filters


# ═══════════════════════════════════════════════════════════════════════════════
# APPLY FILTERS
# ═══════════════════════════════════════════════════════════════════════════════
def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    for col, vals in filters.items():
        if col in df.columns:
            df = df[df[col].isin(vals)]
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="sankey-header">
        <h1>🌊 SankeyPro</h1>
        <p>Gerador Avançado de Diagramas de Sankey — Científico • Modular • Interativo</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Data source ──────────────────────────────────────────────────────────
    df = sidebar_data_section()

    if df is None:
        st.info("👈 Carregue um arquivo CSV/Excel ou clique em **Usar Dataset de Exemplo** para começar.")
        _render_welcome()
        return

    # ── Column selection ─────────────────────────────────────────────────────
    level_cols, value_col, aggregation, sort_by, sort_asc, filter_zero, filters = sidebar_column_selection(df)

    # ── Apply filters ─────────────────────────────────────────────────────────
    df_filtered = apply_filters(df.copy(), filters)

    if df_filtered.empty:
        st.error("Nenhum dado após aplicar os filtros.")
        return

    # ── Build Sankey data ─────────────────────────────────────────────────────
    try:
        sankey_data = build_sankey_data(
            df=df_filtered,
            level_cols=level_cols,
            value_col=value_col,
            aggregation=aggregation,
            sort_by=sort_by,
            sort_ascending=sort_asc,
            filter_zero=filter_zero,
        )
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        return

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_diagram, tab_data, tab_positions, tab_style, tab_export = st.tabs([
        "🌊 Diagrama",
        "📋 Dados",
        "📐 Posições",
        "🎨 Estilo",
        "📥 Exportar",
    ])

    # ────────────────────────────────────────────────────────────────────────
    # TAB: STYLE
    # ────────────────────────────────────────────────────────────────────────
    with tab_style:
        title_input = st.text_input("Título do diagrama", "Diagrama de Sankey", key="diagram_title")
        style_cfg = build_full_config(title=title_input)

    # ────────────────────────────────────────────────────────────────────────
    # TAB: POSITIONS
    # ────────────────────────────────────────────────────────────────────────
    with tab_positions:
        use_manual = st.checkbox("🎛️ Usar posicionamento manual dos nós", False, key="use_manual_pos")

        # Weighted Y option
        value_weighted = st.checkbox("Distribuir nós verticalmente por valor", False, key="value_weighted_y")

        default_x, default_y = auto_layout(sankey_data, value_weighted_y=value_weighted)

        if use_manual:
            node_x, node_y = render_position_editor(sankey_data, default_x, default_y)
            arrangement = "fixed"
        else:
            node_x, node_y = default_x, default_y
            arrangement = style_cfg.get("arrangement", "snap")

    # ────────────────────────────────────────────────────────────────────────
    # BUILD FIGURE
    # ────────────────────────────────────────────────────────────────────────
    try:
        fig = build_sankey_figure(
            sankey_data=sankey_data,
            node_x=node_x if use_manual else None,
            node_y=node_y if use_manual else None,
            palette_name=style_cfg.get("palette_name", "Nature"),
            node_color_by=style_cfg.get("node_color_by", "node"),
            link_color_mode=style_cfg.get("link_color_mode", "source"),
            node_opacity=style_cfg.get("node_opacity", 0.9),
            link_opacity=style_cfg.get("link_opacity", 0.45),
            fixed_link_color=style_cfg.get("fixed_link_color", "#999999"),
            bg_color=style_cfg.get("bg_color", "#FFFFFF"),
            paper_bg=style_cfg.get("paper_bg", "#FFFFFF"),
            node_thickness=style_cfg.get("node_thickness", 20),
            node_pad=style_cfg.get("node_pad", 15),
            node_line_color=style_cfg.get("node_line_color", "#333333"),
            node_line_width=style_cfg.get("node_line_width", 0.8),
            label_format=style_cfg.get("label_format", "name_value"),
            metric_name=style_cfg.get("metric_name", "Valor"),
            metric_abbr=style_cfg.get("metric_abbr", "n"),
            decimal_places=style_cfg.get("decimal_places", 0),
            show_pct_hover=style_cfg.get("show_pct_hover", True),
            show_rank_hover=style_cfg.get("show_rank_hover", False),
            title=style_cfg.get("title", "Diagrama de Sankey"),
            width=style_cfg.get("width", 1100),
            height=style_cfg.get("height", 650),
            margin_l=style_cfg.get("margin_l", 20),
            margin_r=style_cfg.get("margin_r", 20),
            margin_t=style_cfg.get("margin_t", 70),
            margin_b=style_cfg.get("margin_b", 20),
            font_family=style_cfg.get("font_family", "Arial"),
            font_size=style_cfg.get("font_size", 12),
            font_color=style_cfg.get("font_color", "#1A1A1A"),
            title_font_size=style_cfg.get("title_font_size", 17),
            arrangement=arrangement,
        )
        st.session_state["fig"] = fig
    except Exception as e:
        st.error(f"Erro ao construir o diagrama: {e}")
        import traceback; st.code(traceback.format_exc())
        return

    # ────────────────────────────────────────────────────────────────────────
    # TAB: DIAGRAM
    # ────────────────────────────────────────────────────────────────────────
    with tab_diagram:
        _render_metrics(sankey_data, value_col)
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "modeBarButtonsToAdd": ["toggleFullScreen"],
                "toImageButtonOptions": {"format": "png", "scale": 3},
                "responsive": True,
            },
        )
        st.caption(
            f"💡 Fluxo: **{'  →  '.join(level_cols)}**  |  "
            f"Métrica: **{value_col}** ({aggregation})  |  "
            f"Nós: **{len(sankey_data['node_labels'])}**  |  "
            f"Links: **{len(sankey_data['sources'])}**"
        )

    # ────────────────────────────────────────────────────────────────────────
    # TAB: DATA
    # ────────────────────────────────────────────────────────────────────────
    with tab_data:
        _render_data_tab(df_filtered, sankey_data, level_cols, value_col, aggregation)

    # ────────────────────────────────────────────────────────────────────────
    # TAB: EXPORT
    # ────────────────────────────────────────────────────────────────────────
    with tab_export:
        render_export_panel(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _render_metrics(sankey_data: dict, value_col: str):
    """Render summary metric cards."""
    grand_total = sankey_data["grand_total"]
    n_nodes = len(sankey_data["node_labels"])
    n_links = len(sankey_data["sources"])
    n_levels = sankey_data["n_levels"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Geral", f"{grand_total:,.0f}", help=f"Soma de {value_col}")
    with col2:
        st.metric("Nós", n_nodes)
    with col3:
        st.metric("Links", n_links)
    with col4:
        st.metric("Níveis", n_levels)


def _render_data_tab(df: pd.DataFrame, sankey_data: dict, level_cols, value_col, aggregation):
    """Data explorer tab content."""
    st.markdown("### 📋 Dados Originais (filtrados)")
    st.dataframe(df, use_container_width=True, height=300)

    st.markdown("### 📊 Tabela Agregada do Sankey")
    agg_func = {"sum": "sum", "mean": "mean", "count": "count", "max": "max", "min": "min"}.get(aggregation, "sum")
    agg_df = df.groupby(level_cols, observed=True)[value_col].agg(agg_func).reset_index()
    agg_df.columns = list(level_cols) + [f"{value_col} ({aggregation})"]
    agg_df = agg_df.sort_values(f"{value_col} ({aggregation})", ascending=False)
    st.dataframe(agg_df, use_container_width=True, height=300)

    st.markdown("### 📈 Resumo por Nó")
    rows = []
    for label in sankey_data["node_labels"]:
        col_name, val_name = label.split("::", 1)
        lvl = sankey_data["node_level"][label]
        total = sankey_data["node_totals"][label]
        pct = total / sankey_data["grand_total"] * 100 if sankey_data["grand_total"] > 0 else 0
        rows.append({
            "Nível": lvl + 1,
            "Coluna": col_name,
            "Nó": val_name,
            f"{value_col} ({aggregation})": round(total, 3),
            "% do Total": round(pct, 2),
        })
    summary_df = pd.DataFrame(rows).sort_values(["Nível", f"{value_col} ({aggregation})"], ascending=[True, False])
    st.dataframe(summary_df, use_container_width=True, height=300)

    # Download aggregated table
    csv = agg_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar tabela agregada (CSV)", csv, "sankey_aggregated.csv", "text/csv", key="dl_agg_csv")


def _render_welcome():
    """Welcome / instructions screen."""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f8faff 0%, #eef4ff 100%);
        border: 1px solid #d0e0ff;
        border-radius: 14px;
        padding: 32px;
        margin-top: 10px;
    ">
    <h2 style="color:#1a3a5c; margin-top:0">🌊 Como usar o SankeyPro</h2>
    <ol style="color:#2d4a6a; line-height:2">
        <li><b>Carregue seu arquivo</b> CSV ou Excel — ou use o dataset de exemplo ecológico.</li>
        <li><b>Selecione as colunas de nível</b> na barra lateral (ex: Bacia → Espécie → Sexo).</li>
        <li><b>Escolha a coluna de valores</b> (ex: Abundância, Biomassa, CPUE).</li>
        <li><b>Personalize</b> o visual na aba <em>🎨 Estilo</em>: paletas, fontes, transparência, layout.</li>
        <li><b>Ajuste posições</b> dos nós na aba <em>📐 Posições</em> se desejar controle total.</li>
        <li><b>Exporte</b> em PNG, SVG, PDF ou HTML interativo.</li>
    </ol>
    </div>

    <div style="display:flex; gap:16px; margin-top:20px; flex-wrap:wrap;">
        <div style="flex:1; min-width:200px; background:#f0fff4; border:1px solid #b7e4c7; border-radius:10px; padding:20px;">
            <h4 style="color:#1b4332; margin:0 0 8px">✅ Funcionalidades</h4>
            <ul style="color:#2d6a4f; margin:0; padding-left:18px; line-height:1.8">
                <li>Níveis ilimitados</li>
                <li>Hover científico detalhado</li>
                <li>7 templates visuais</li>
                <li>Posicionamento manual de nós</li>
                <li>Exportação vetorial (SVG/PDF)</li>
                <li>Filtros interativos</li>
            </ul>
        </div>
        <div style="flex:1; min-width:200px; background:#fff8f0; border:1px solid #fcd5a0; border-radius:10px; padding:20px;">
            <h4 style="color:#7d3c0a; margin:0 0 8px">📊 Métricas Suportadas</h4>
            <ul style="color:#a04000; margin:0; padding-left:18px; line-height:1.8">
                <li>Abundância / Biomassa</li>
                <li>CPUE / Frequência</li>
                <li>Densidade / Proporção</li>
                <li>Qualquer coluna numérica</li>
            </ul>
        </div>
        <div style="flex:1; min-width:200px; background:#f3f0ff; border:1px solid #c9b8ff; border-radius:10px; padding:20px;">
            <h4 style="color:#3b1f8c; margin:0 0 8px">🎨 Personalização</h4>
            <ul style="color:#5b3faa; margin:0; padding-left:18px; line-height:1.8">
                <li>10 paletas de cores</li>
                <li>12 famílias de fonte</li>
                <li>Opacidade adaptativa</li>
                <li>Modo dark/light</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
