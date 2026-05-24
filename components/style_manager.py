"""
style_manager.py
Renders all Streamlit style controls and returns a config dict
consumed by sankey_builder.build_sankey_figure().
"""

import streamlit as st
from typing import Dict, Any
from utils.color_utils import PALETTES, TEMPLATES


FONT_FAMILIES = [
    "Arial", "Helvetica Neue", "Times New Roman", "Georgia",
    "Verdana", "Courier New", "Tahoma", "Trebuchet MS",
    "Palatino", "Garamond", "Gill Sans", "Century Gothic",
]

ARRANGEMENT_OPTIONS = {
    "Snap (padrão)": "snap",
    "Fixed (posição manual)": "fixed",
    "Perpendicular": "perpendicular",
    "Freeform (arrastar)": "freeform",
}

LABEL_FORMATS = {
    "Nome + Valor  →  Tapajós (120)": "name_value",
    "Somente Nome  →  Tapajós": "name_only",
    "Nome + n  →  Tapajós  n=120": "name_n",
    "Nome + %  →  Tapajós (32%)": "name_pct",
}

LINK_COLOR_MODES = {
    "Herdar da Origem": "source",
    "Herdar do Destino": "target",
    "Gradiente": "gradient",
    "Cor Fixa": "fixed",
}

NODE_COLOR_BY = {
    "Por Nó (individual)": "node",
    "Por Nível": "level",
    "Manual": "manual",
}


def render_template_selector() -> Dict[str, Any]:
    """Render template selector and return its settings."""
    st.markdown("### 🎨 Template Visual")
    template_key = st.selectbox(
        "Escolha um template base",
        options=list(TEMPLATES.keys()),
        format_func=lambda k: {
            "publication": "📄 Publication",
            "minimal": "⬜ Minimal",
            "dark": "🌑 Dark",
            "nature": "🌿 Nature",
            "scientific": "🔬 Scientific",
            "pastel": "🎀 Pastel",
            "high_contrast": "⚡ High Contrast",
        }.get(k, k.title()),
        key="template_selector",
    )
    return TEMPLATES[template_key].copy()


def render_font_settings(defaults: Dict) -> Dict[str, Any]:
    """Render font controls and return settings dict."""
    st.markdown("### 🔤 Fontes")
    with st.expander("Configurações de Fonte", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            font_family = st.selectbox("Família", FONT_FAMILIES,
                index=FONT_FAMILIES.index(defaults.get("font_family", "Arial"))
                if defaults.get("font_family", "Arial") in FONT_FAMILIES else 0,
                key="font_family")
            font_size = st.slider("Tamanho (nós)", 8, 22, int(defaults.get("font_size", 12)), key="font_size")
        with c2:
            font_color = st.color_picker("Cor da fonte", defaults.get("font_color", "#1A1A1A"), key="font_color")
            title_font_size = st.slider("Tamanho (título)", 12, 32, int(defaults.get("title_font_size", 17)), key="title_font_size")
    return dict(
        font_family=font_family,
        font_size=font_size,
        font_color=font_color,
        title_font_size=title_font_size,
    )


def render_color_settings(defaults: Dict) -> Dict[str, Any]:
    """Render color/palette controls."""
    st.markdown("### 🌈 Cores")
    with st.expander("Configurações de Cor", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            palette_name = st.selectbox("Paleta", list(PALETTES.keys()),
                index=list(PALETTES.keys()).index(defaults.get("palette", "Nature"))
                if defaults.get("palette", "Nature") in PALETTES else 0,
                key="palette_name")
            node_color_by = st.selectbox("Cor dos nós por", list(NODE_COLOR_BY.keys()),
                format_func=lambda x: x, key="node_color_by_label")
            node_color_by_val = NODE_COLOR_BY[node_color_by]

        with c2:
            link_color_mode = st.selectbox("Cor dos links", list(LINK_COLOR_MODES.keys()),
                format_func=lambda x: x, key="link_color_mode_label")
            link_color_mode_val = LINK_COLOR_MODES[link_color_mode]
            fixed_link_color = st.color_picker("Cor fixa (se aplicável)", "#999999", key="fixed_link_color")

        c3, c4 = st.columns(2)
        with c3:
            node_opacity = st.slider("Opacidade dos nós", 0.1, 1.0, float(defaults.get("node_opacity", 0.9)), 0.05, key="node_opacity")
            bg_color = st.color_picker("Cor de fundo", defaults.get("bg_color", "#FFFFFF"), key="bg_color")
        with c4:
            link_opacity = st.slider("Opacidade dos links", 0.05, 1.0, float(defaults.get("link_opacity", 0.45)), 0.05, key="link_opacity")
            paper_bg = st.color_picker("Cor do papel", defaults.get("paper_bg", "#FFFFFF"), key="paper_bg")

    return dict(
        palette_name=palette_name,
        node_color_by=node_color_by_val,
        link_color_mode=link_color_mode_val,
        fixed_link_color=fixed_link_color,
        node_opacity=node_opacity,
        link_opacity=link_opacity,
        bg_color=bg_color,
        paper_bg=paper_bg,
    )


def render_node_style(defaults: Dict) -> Dict[str, Any]:
    """Render node style controls."""
    st.markdown("### 🟦 Estilo dos Nós")
    with st.expander("Configurações dos Nós", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            node_thickness = st.slider("Espessura", 5, 50, int(defaults.get("node_thickness", 20)), key="node_thickness")
            node_pad = st.slider("Espaçamento", 2, 40, int(defaults.get("node_pad", 15)), key="node_pad")
        with c2:
            node_line_color = st.color_picker("Cor da borda", defaults.get("node_line_color", "#333333"), key="node_line_color")
            node_line_width = st.slider("Espessura borda", 0.0, 3.0, float(defaults.get("node_line_width", 0.8)), 0.1, key="node_line_width")
        with c3:
            label_format_label = st.selectbox("Formato do rótulo", list(LABEL_FORMATS.keys()), key="label_format_label")
            label_format = LABEL_FORMATS[label_format_label]
            decimal_places = st.slider("Casas decimais", 0, 4, 0, key="decimal_places")
    return dict(
        node_thickness=node_thickness,
        node_pad=node_pad,
        node_line_color=node_line_color,
        node_line_width=node_line_width,
        label_format=label_format,
        decimal_places=decimal_places,
    )


def render_layout_settings() -> Dict[str, Any]:
    """Render diagram layout controls."""
    st.markdown("### 📐 Layout do Gráfico")
    with st.expander("Configurações de Layout", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            width = st.slider("Largura (px)", 600, 2400, 1100, 50, key="diag_width")
            height = st.slider("Altura (px)", 300, 1600, 650, 50, key="diag_height")
            arrangement_label = st.selectbox("Arranjo dos nós", list(ARRANGEMENT_OPTIONS.keys()), key="arrangement_label")
            arrangement = ARRANGEMENT_OPTIONS[arrangement_label]
        with c2:
            margin_l = st.slider("Margem esquerda", 0, 100, 20, key="margin_l")
            margin_r = st.slider("Margem direita", 0, 100, 20, key="margin_r")
            margin_t = st.slider("Margem superior", 20, 150, 70, key="margin_t")
            margin_b = st.slider("Margem inferior", 0, 100, 20, key="margin_b")
    return dict(
        width=width,
        height=height,
        arrangement=arrangement,
        margin_l=margin_l,
        margin_r=margin_r,
        margin_t=margin_t,
        margin_b=margin_b,
    )


def render_hover_settings() -> Dict[str, Any]:
    """Render hover/label info controls."""
    st.markdown("### 💬 Informações do Hover")
    with st.expander("Configurações de Hover", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            metric_name = st.text_input("Nome da métrica", "Abundância", key="metric_name")
            metric_abbr = st.text_input("Abreviação (para rótulos)", "n", key="metric_abbr")
        with c2:
            show_pct_hover = st.checkbox("Mostrar % no hover", True, key="show_pct_hover")
            show_rank_hover = st.checkbox("Mostrar rank no hover", False, key="show_rank_hover")
    return dict(
        metric_name=metric_name,
        metric_abbr=metric_abbr,
        show_pct_hover=show_pct_hover,
        show_rank_hover=show_rank_hover,
    )


def build_full_config(title: str = "Diagrama de Sankey") -> Dict[str, Any]:
    """
    Render all style panels and return a unified config dict
    ready to unpack into build_sankey_figure().
    """
    template_cfg = render_template_selector()
    st.divider()
    font_cfg = render_font_settings(template_cfg)
    st.divider()
    color_cfg = render_color_settings(template_cfg)
    st.divider()
    node_cfg = render_node_style(template_cfg)
    st.divider()
    layout_cfg = render_layout_settings()
    st.divider()
    hover_cfg = render_hover_settings()

    return {
        "title": title,
        **font_cfg,
        **color_cfg,
        **node_cfg,
        **layout_cfg,
        **hover_cfg,
    }
