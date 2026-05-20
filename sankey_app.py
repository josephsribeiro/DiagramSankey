"""
================================================================================
  SANKEY CHART GENERATOR — Aplicativo Streamlit Interativo
================================================================================
  Instalação:
    pip install streamlit plotly pandas openpyxl kaleido

  Execução:
    streamlit run sankey_app.py

  Autor: Gerado com assistência de Claude (Anthropic)
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import io
import base64
from copy import deepcopy

# ─────────────────────────────────────────────────────────────────────────────
# VERIFICAÇÃO DO KALEIDO
# ─────────────────────────────────────────────────────────────────────────────
try:
    import kaleido
    KALEIDO_AVAILABLE = True
except ImportError:
    KALEIDO_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sankey Chart Generator",
    page_icon="🔀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS PERSONALIZADO — estilo limpo e profissional
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main-title {
    font-family: 'Sora', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #1a73e8, #0d47a1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
  }
  .subtitle {
    font-size: 1rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
  }
  .section-header {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
    border-left: 4px solid #1a73e8;
    padding-left: 10px;
    margin: 1.2rem 0 0.7rem 0;
  }
  .info-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.88rem;
    color: #1e40af;
    line-height: 1.6;
  }
  .stButton > button {
    background: linear-gradient(135deg, #1a73e8, #1558c0);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(26,115,232,0.35);
  }
  .stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #047857);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
  }
  div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    margin-bottom: 0.5rem;
  }
  .metric-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .metric-value { font-size: 1.6rem; font-weight: 700; color: #1a73e8; }
  .metric-label { font-size: 0.78rem; color: #6b7280; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DADOS DE EXEMPLO
# ─────────────────────────────────────────────────────────────────────────────
EXEMPLO_DADOS = pd.DataFrame({
    "source": [
        "Receita Total", "Receita Total",
        "Produto A", "Produto A", "Produto B", "Produto B",
        "Brasil", "EUA", "Brasil", "EUA"
    ],
    "target": [
        "Produto A", "Produto B",
        "Brasil", "EUA", "Brasil", "EUA",
        "Lucro", "Lucro", "Custo", "Custo"
    ],
    "value": [60, 40, 35, 25, 20, 20, 30, 30, 25, 15],
})

PALETA_CORES = [
    "#1a73e8", "#e8711a", "#34a853", "#ea4335", "#9b27af",
    "#00acc1", "#f4b400", "#0d47a1", "#e65100", "#1b5e20",
    "#4a148c", "#006064", "#f57f17", "#37474f", "#880e4f",
]

# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────

def validar_dados(df: pd.DataFrame) -> tuple[bool, str]:
    """Valida se o DataFrame possui as colunas obrigatórias e dados coerentes."""
    colunas_req = {"source", "target", "value"}
    colunas_df = set(df.columns.str.lower().str.strip())
    if not colunas_req.issubset(colunas_df):
        faltando = colunas_req - colunas_df
        return False, f"Colunas ausentes: {', '.join(faltando)}"
    df.columns = df.columns.str.lower().str.strip()
    if df["value"].isnull().any():
        return False, "Coluna 'value' contém valores nulos."
    if (pd.to_numeric(df["value"], errors="coerce") < 0).any():
        return False, "Coluna 'value' contém valores negativos."
    if df["source"].isnull().any() or df["target"].isnull().any():
        return False, "Colunas 'source' ou 'target' contêm valores nulos."
    return True, "OK"


def normalizar_para_percentual(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza os valores para que a soma total seja 100%."""
    df = df.copy()
    total = df["value"].sum()
    if total > 0:
        df["value"] = (df["value"] / total * 100).round(2)
    return df


def construir_sankey(
    df: pd.DataFrame,
    titulo: str,
    subtitulo: str,
    mostrar_rotulos: bool,
    mostrar_valores_links: bool,
    usar_percentual: bool,
    altura: int,
    largura: int,
    cores_nos: dict,
    opacidade_link: float,
    orientacao: str,
) -> go.Figure:
    """Constrói a figura Plotly Sankey a partir do DataFrame de fluxos."""

    if usar_percentual:
        df = normalizar_para_percentual(df)

    # Cria lista única de nós na ordem de aparição
    todos_nos = pd.unique(df[["source", "target"]].values.ravel()).tolist()
    no_index = {no: i for i, no in enumerate(todos_nos)}

    # Índices de origem e destino
    fontes = df["source"].map(no_index).tolist()
    destinos = df["target"].map(no_index).tolist()
    valores = df["value"].tolist()

    # Cores dos nós — usa mapeamento personalizado ou paleta padrão
    cor_nos = []
    for i, no in enumerate(todos_nos):
        if no in cores_nos and cores_nos[no]:
            cor_nos.append(cores_nos[no])
        else:
            cor_nos.append(PALETA_CORES[i % len(PALETA_CORES)])

    # Cores dos links (versão transparente da cor de origem)
    def hex_para_rgba(hex_cor: str, alpha: float) -> str:
        hex_cor = hex_cor.lstrip("#")
        r, g, b = tuple(int(hex_cor[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r},{g},{b},{alpha})"

    cor_links = [hex_para_rgba(cor_nos[s], opacidade_link) for s in fontes]

    # Labels dos links (opcional)
    if mostrar_valores_links:
        sufixo = "%" if usar_percentual else ""
        label_links = [f"{v:.1f}{sufixo}" for v in valores]
    else:
        label_links = [""] * len(valores)

    # Rótulos dos nós
    if mostrar_rotulos:
        labels_nos = todos_nos
    else:
        labels_nos = [""] * len(todos_nos)

    # Tooltip com valor
    sufixo = "%" if usar_percentual else ""
    customdata_links = [
        f"<b>{df['source'].iloc[i]}</b> → <b>{df['target'].iloc[i]}</b><br>"
        f"Valor: {valores[i]:.2f}{sufixo}"
        for i in range(len(valores))
    ]

    fig = go.Figure(go.Sankey(
        orientation=orientacao,
        arrangement="snap",
        node=dict(
            pad=18,
            thickness=22,
            line=dict(color="white", width=0.5),
            label=labels_nos,
            color=cor_nos,
            hovertemplate="<b>%{label}</b><br>Fluxo total: %{value:.2f}" + sufixo + "<extra></extra>",
        ),
        link=dict(
            source=fontes,
            target=destinos,
            value=valores,
            color=cor_links,
            label=label_links,
            customdata=customdata_links,
            hovertemplate="%{customdata}<extra></extra>",
        ),
    ))

    titulo_completo = titulo
    if subtitulo:
        titulo_completo += f"<br><span style='font-size:13px;color:#6b7280'>{subtitulo}</span>"

    fig.update_layout(
        title=dict(
            text=titulo_completo,
            font=dict(size=20, family="Sora, sans-serif", color="#1e293b"),
            x=0.01,
        ),
        font=dict(family="Inter, sans-serif", size=12, color="#374151"),
        height=altura,
        width=largura if largura > 0 else None,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=30, r=30, t=70, b=30),
    )
    return fig


def exportar_html(fig: go.Figure) -> bytes:
    """Exporta a figura como HTML interativo."""
    buffer = io.StringIO()
    fig.write_html(buffer, include_plotlyjs="cdn", full_html=True)
    return buffer.getvalue().encode("utf-8")


def exportar_png(fig: go.Figure) -> bytes:
    """Exporta a figura como PNG."""
    
    if not KALEIDO_AVAILABLE:
        return None

    try:
        return fig.to_image(format="png", scale=1)
    except Exception:
        return None


def exportar_jpg_300dpi(fig: go.Figure) -> bytes:
    """Exporta JPEG 300 DPI."""

    if not KALEIDO_AVAILABLE:
        return None

    try:
        return fig.to_image(format="jpeg", scale=3.125)
    except Exception:
        return None 
    """
    Exporta a figura como JPEG em alta resolução (~300 DPI).
    O Plotly/kaleido renderiza a 96 DPI internamente; para atingir 300 DPI
    usamos scale = 300/96 ≈ 3.125, o que triplica a resolução de pixel.
    Requer kaleido.
    """
    try:
        # scale ≈ 3.125 → ~300 DPI a partir da base de 96 DPI do kaleido
        return fig.to_image(format="jpeg", scale=3.125)
    except Exception:
        return None


 def exportar_svg(fig: go.Figure) -> bytes:
    """Exporta SVG."""

    if not KALEIDO_AVAILABLE:
        return None

    try:
        return fig.to_image(format="svg")
    except Exception:
        return None
    """
    Exporta a figura como SVG vetorial (resolução independente).
    Requer kaleido. SVGs são ideais para edição em Illustrator/Inkscape.
    """
    try:
        return fig.to_image(format="svg")
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# ESTADO DA SESSÃO
# ─────────────────────────────────────────────────────────────────────────────
if "df_fluxos" not in st.session_state:
    st.session_state["df_fluxos"] = EXEMPLO_DADOS.copy()
if "cores_nos" not in st.session_state:
    st.session_state["cores_nos"] = {}

# ─────────────────────────────────────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────────────────────────────────────
col_head, col_logo = st.columns([5, 1])
with col_head:
    st.markdown('<div class="main-title">🔀 Sankey Chart Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Crie diagramas de Sankey interativos a partir de dados CSV, Excel ou entrada manual.</div>', unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT PRINCIPAL: sidebar (controles) + área principal (gráfico)
# ─────────────────────────────────────────────────────────────────────────────
sidebar = st.sidebar

# ══════════════════════════════════════════════════
# SIDEBAR — CONFIGURAÇÕES
# ══════════════════════════════════════════════════
sidebar.markdown("## ⚙️ Configurações")

# ── Título e Subtítulo ──
sidebar.markdown('<div class="section-header">📝 Rótulos</div>', unsafe_allow_html=True)
titulo = sidebar.text_input("Título do gráfico", value="Diagrama de Sankey")
subtitulo = sidebar.text_input("Subtítulo (opcional)", value="")

# ── Dimensões ──
sidebar.markdown('<div class="section-header">📐 Dimensões</div>', unsafe_allow_html=True)
altura = sidebar.slider("Altura (px)", 400, 1200, 600, step=50)
largura_auto = sidebar.checkbox("Largura automática", value=True)
largura = 0
if not largura_auto:
    largura = sidebar.slider("Largura (px)", 600, 2000, 1000, step=50)

# ── Estilo ──
sidebar.markdown('<div class="section-header">🎨 Estilo</div>', unsafe_allow_html=True)
mostrar_rotulos = sidebar.checkbox("Mostrar rótulos nos nós", value=True)
mostrar_valores_links = sidebar.checkbox("Mostrar valores nos links", value=False)
usar_percentual = sidebar.checkbox("Normalizar para percentual (%)", value=False)
opacidade_link = sidebar.slider("Opacidade dos links", 0.1, 0.9, 0.45, step=0.05)
orientacao = sidebar.selectbox("Orientação", ["h", "v"], format_func=lambda x: "Horizontal" if x == "h" else "Vertical")

# ─────────────────────────────────────────────────────────────────────────────
# ÁREA PRINCIPAL — ABAS
# ─────────────────────────────────────────────────────────────────────────────
tab_dados, tab_grafico, tab_ajuda = st.tabs(["📊 Dados", "📈 Gráfico", "❓ Ajuda"])

# ══════════════════════════════════════════════════
# ABA: DADOS
# ══════════════════════════════════════════════════
with tab_dados:
    col_upload, col_manual = st.columns([1, 1], gap="large")

    # ── Upload de arquivo ──
    with col_upload:
        st.markdown('<div class="section-header">📁 Importar arquivo</div>', unsafe_allow_html=True)
        arquivo = st.file_uploader(
            "Faça upload de CSV ou Excel",
            type=["csv", "xlsx", "xls"],
            help="O arquivo deve conter as colunas: source, target, value",
        )
        if arquivo:
            try:
                if arquivo.name.endswith(".csv"):
                    df_up = pd.read_csv(arquivo)
                else:
                    df_up = pd.read_excel(arquivo)

                df_up.columns = df_up.columns.str.lower().str.strip()
                ok, msg = validar_dados(df_up)
                if ok:
                    st.session_state["df_fluxos"] = df_up[["source", "target", "value"]].copy()
                    st.session_state["df_fluxos"]["value"] = pd.to_numeric(
                        st.session_state["df_fluxos"]["value"], errors="coerce"
                    ).fillna(0)
                    st.success(f"✅ Arquivo carregado: {len(df_up)} linhas")
                else:
                    st.error(f"❌ Erro de validação: {msg}")
            except Exception as e:
                st.error(f"❌ Falha ao ler arquivo: {e}")

        st.markdown("**Formato esperado:**")
        st.dataframe(
            pd.DataFrame({"source": ["A", "A"], "target": ["B", "C"], "value": [60, 40]}),
            use_container_width=True,
            hide_index=True,
        )

        # Download do template
        template = pd.DataFrame({
            "source": ["Categoria 1", "Categoria 1", "Categoria 2"],
            "target": ["Sub A", "Sub B", "Sub C"],
            "value": [50, 30, 20],
        })
        buf_csv = io.StringIO()
        template.to_csv(buf_csv, index=False)
        st.download_button(
            "⬇️ Baixar template CSV",
            data=buf_csv.getvalue().encode("utf-8"),
            file_name="template_sankey.csv",
            mime="text/csv",
        )

    # ── Edição manual ──
    with col_manual:
        st.markdown('<div class="section-header">✏️ Edição manual dos fluxos</div>', unsafe_allow_html=True)
        st.caption("Edite, adicione ou remova linhas diretamente na tabela abaixo.")

        df_editado = st.data_editor(
            st.session_state["df_fluxos"],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "source": st.column_config.TextColumn("Origem", help="Nó de origem"),
                "target": st.column_config.TextColumn("Destino", help="Nó de destino"),
                "value": st.column_config.NumberColumn(
                    "Valor", min_value=0, format="%.2f", help="Valor do fluxo"
                ),
            },
            key="editor_fluxos",
        )

        if st.button("💾 Aplicar edições", use_container_width=True):
            ok, msg = validar_dados(df_editado)
            if ok:
                st.session_state["df_fluxos"] = df_editado.copy()
                st.success("✅ Dados atualizados!")
            else:
                st.error(f"❌ {msg}")

        if st.button("🔄 Restaurar exemplo padrão", use_container_width=True):
            st.session_state["df_fluxos"] = EXEMPLO_DADOS.copy()
            st.session_state["cores_nos"] = {}
            st.rerun()

    # ── Métricas resumo ──
    st.divider()
    df_atual = st.session_state["df_fluxos"]
    todos_nos_atual = pd.unique(df_atual[["source", "target"]].values.ravel()).tolist()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df_atual)}</div><div class="metric-label">Conexões</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(todos_nos_atual)}</div><div class="metric-label">Nós únicos</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df_atual["value"].sum():.1f}</div><div class="metric-label">Soma dos valores</div></div>', unsafe_allow_html=True)
    with m4:
        fontes_unicas = df_atual["source"].nunique()
        st.markdown(f'<div class="metric-card"><div class="metric-value">{fontes_unicas}</div><div class="metric-label">Origens distintas</div></div>', unsafe_allow_html=True)

    # ── Cores personalizadas por nó ──
    st.divider()
    st.markdown('<div class="section-header">🎨 Cores por nó (opcional)</div>', unsafe_allow_html=True)
    st.caption("Selecione uma cor para cada nó. Deixe em branco para usar a paleta automática.")

    cols_cor = st.columns(min(len(todos_nos_atual), 4))
    for i, no in enumerate(todos_nos_atual):
        cor_atual = st.session_state["cores_nos"].get(no, PALETA_CORES[i % len(PALETA_CORES)])
        nova_cor = cols_cor[i % 4].color_picker(
            f"`{no}`", value=cor_atual, key=f"cor_{no}"
        )
        st.session_state["cores_nos"][no] = nova_cor


# ══════════════════════════════════════════════════
# ABA: GRÁFICO
# ══════════════════════════════════════════════════
with tab_grafico:
    df_grafico = st.session_state["df_fluxos"].copy()
    ok, msg = validar_dados(df_grafico)

    if not ok:
        st.error(f"❌ Dados inválidos: {msg}")
    elif df_grafico.empty:
        st.warning("⚠️ Nenhum dado disponível. Insira dados na aba **Dados**.")
    else:
        df_grafico["value"] = pd.to_numeric(df_grafico["value"], errors="coerce").fillna(0)
        df_grafico = df_grafico[df_grafico["value"] > 0]

        with st.spinner("Gerando gráfico..."):
            fig = construir_sankey(
                df=df_grafico,
                titulo=titulo,
                subtitulo=subtitulo,
                mostrar_rotulos=mostrar_rotulos,
                mostrar_valores_links=mostrar_valores_links,
                usar_percentual=usar_percentual,
                altura=altura,
                largura=largura,
                cores_nos=st.session_state["cores_nos"],
                opacidade_link=opacidade_link,
                orientacao=orientacao,
            )

        st.plotly_chart(fig, use_container_width=largura_auto)

        # ── Exportação ──
        st.divider()
        st.markdown('<div class="section-header">⬇️ Exportar gráfico</div>', unsafe_allow_html=True)

        # Gera todos os formatos uma única vez (evita múltiplos renders)
        _kaleido_ok = None  # será resolvido na primeira tentativa

        def _checar_kaleido(fig):
            """Tenta gerar PNG simples para verificar se kaleido está disponível."""
            try:
                fig.to_image(format="png", scale=1)
                return True
            except Exception:
                return False

        col_ex1, col_ex2, col_ex3, col_ex4, col_ex5 = st.columns(5)

        # ── HTML ──
        with col_ex1:
            html_bytes = exportar_html(fig)
            st.download_button(
                "🌐 HTML",
                data=html_bytes,
                file_name="sankey.html",
                mime="text/html",
                use_container_width=True,
                help="HTML interativo — abre em qualquer navegador sem instalar nada.",
            )

        # ── PNG ──
        with col_ex2:
            png_bytes = exportar_png(fig)
            if png_bytes:
                st.download_button(
                    "🖼️ PNG",
                    data=png_bytes,
                    file_name="sankey.png",
                    mime="image/png",
                    use_container_width=True,
                    help="Imagem PNG em resolução padrão (96 DPI).",
                )
            else:
                st.button(
                    "🖼️ PNG",
                    disabled=True,
                    use_container_width=True,
                    help="Requer `pip install kaleido`",
                )

        # ── JPG 300 DPI ──
        with col_ex3:
            jpg_bytes = exportar_jpg_300dpi(fig)
            if jpg_bytes:
                st.download_button(
                    "📷 JPG 300 DPI",
                    data=jpg_bytes,
                    file_name="sankey_300dpi.jpg",
                    mime="image/jpeg",
                    use_container_width=True,
                    help="JPEG em alta resolução (~300 DPI) — ideal para impressão.",
                )
            else:
                st.button(
                    "📷 JPG 300 DPI",
                    disabled=True,
                    use_container_width=True,
                    help="Requer `pip install kaleido`",
                )

        # ── SVG ──
        with col_ex4:
            svg_bytes = exportar_svg(fig)
            if svg_bytes:
                st.download_button(
                    "✏️ SVG",
                    data=svg_bytes,
                    file_name="sankey.svg",
                    mime="image/svg+xml",
                    use_container_width=True,
                    help="Vetor SVG escalável — edite no Illustrator ou Inkscape.",
                )
            else:
                st.button(
                    "✏️ SVG",
                    disabled=True,
                    use_container_width=True,
                    help="Requer `pip install kaleido`",
                )

        # ── CSV ──
        with col_ex5:
            buf_csv2 = io.StringIO()
            df_grafico.to_csv(buf_csv2, index=False)
            st.download_button(
                "📄 CSV",
                data=buf_csv2.getvalue().encode("utf-8"),
                file_name="sankey_dados.csv",
                mime="text/csv",
                use_container_width=True,
                help="Dados dos fluxos em formato CSV.",
            )

        # Aviso único caso kaleido não esteja instalado
        if not (png_bytes or jpg_bytes or svg_bytes):
            st.warning(
                "⚠️ **kaleido** não encontrado — exportações de imagem (PNG, JPG, SVG) estão desativadas. "
                "Instale com: `pip install kaleido`",
                icon="📦",
            )


# ══════════════════════════════════════════════════
# ABA: AJUDA
# ══════════════════════════════════════════════════
with tab_ajuda:
    st.markdown("## 📖 Como usar o Sankey Chart Generator")

    with st.expander("🔍 O que é um diagrama de Sankey?", expanded=True):
        st.markdown("""
        Um **diagrama de Sankey** é uma visualização de fluxos entre categorias.
        A largura de cada seta é proporcional ao valor do fluxo — quanto mais larga, maior o volume.

        São muito usados para representar:
        - Fluxo de energia ou dinheiro
        - Jornada do cliente (funil de vendas)
        - Distribuição de orçamentos
        - Análise de processos industriais
        """)

    with st.expander("📁 Formato dos dados"):
        st.markdown("""
        O arquivo (CSV ou Excel) deve conter **3 colunas obrigatórias**:

        | Coluna   | Tipo   | Descrição                        |
        |----------|--------|----------------------------------|
        | `source` | texto  | Nó de origem do fluxo            |
        | `target` | texto  | Nó de destino do fluxo           |
        | `value`  | número | Magnitude do fluxo (≥ 0)         |

        **Exemplo:**
        ```
        source,target,value
        Receita,Produto A,60
        Receita,Produto B,40
        Produto A,Brasil,35
        Produto A,EUA,25
        ```
        """)

    with st.expander("🎨 Personalização de cores"):
        st.markdown("""
        - Na aba **Dados**, role até **Cores por nó** e clique no seletor de cor de cada nó.
        - Se não selecionar uma cor, o sistema atribui cores automaticamente da paleta padrão.
        - A cor dos **links** é derivada automaticamente da cor do nó de origem, com transparência ajustável pelo slider **Opacidade dos links** na barra lateral.
        """)

    with st.expander("📐 Dicas de desempenho para grandes volumes"):
        st.markdown("""
        - Evite grafos com mais de **200 nós** ou **500 links** para manter a interatividade fluida.
        - Use a opção **Normalizar para %** quando os valores absolutos forem muito grandes.
        - Para conjuntos maiores, agrupe nós de menor relevância em uma categoria "Outros".
        - O export HTML mantém toda a interatividade e pode ser compartilhado sem instalar nada.
        """)

    with st.expander("⬇️ Instalação e execução"):
        st.code("""
# 1. Instale as dependências
pip install streamlit plotly pandas openpyxl kaleido

# 2. Execute o aplicativo
streamlit run sankey_app.py

# 3. Acesse no navegador (abre automaticamente)
# http://localhost:8501
        """, language="bash")

    with st.expander("🖼️ Formatos de exportação disponíveis"):
        st.markdown("""
        | Formato | Botão | Descrição | Requer |
        |---|---|---|---|
        | **HTML** | 🌐 HTML | Interativo, abre em qualquer navegador | — |
        | **PNG** | 🖼️ PNG | Imagem rasterizada (~96 DPI) | `kaleido` |
        | **JPG 300 DPI** | 📷 JPG 300 DPI | Alta resolução para impressão | `kaleido` |
        | **SVG** | ✏️ SVG | Vetor escalável, editável no Illustrator/Inkscape | `kaleido` |
        | **CSV** | 📄 CSV | Dados dos fluxos em texto | — |

        > **Nota sobre DPI:** o kaleido renderiza internamente a 96 DPI.
        > Para atingir 300 DPI, usamos `scale = 3.125` (≈ 300/96), triplicando
        > a resolução de pixel sem perda de qualidade.
        > O SVG é vetorial e, por definição, tem resolução infinita.
        """)

    st.markdown("---")
    st.caption("Desenvolvido com ❤️ usando Streamlit + Plotly · Assistência: Claude (Anthropic)")
