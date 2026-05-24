"""
export_manager.py
Handles exporting the Sankey figure to PNG, SVG, HTML, and PDF.
Uses Plotly's kaleido engine for static exports.
"""

import io
import base64
import streamlit as st
import plotly.graph_objects as go
from typing import Optional


def try_import_kaleido() -> bool:
    try:
        import kaleido
        return True
    except ImportError:
        return False


def export_to_html(fig: go.Figure, filename: str = "sankey.html") -> bytes:
    """Export figure to standalone interactive HTML."""
    html_str = fig.to_html(
        full_html=True,
        include_plotlyjs="cdn",
        config={"displayModeBar": True, "responsive": True},
    )
    return html_str.encode("utf-8")


def export_to_png(fig: go.Figure, scale: int = 3, width: Optional[int] = None, height: Optional[int] = None) -> Optional[bytes]:
    """Export figure to PNG bytes at given scale (DPI-equivalent)."""
    try:
        kwargs = {"format": "png", "scale": scale}
        if width:
            kwargs["width"] = width
        if height:
            kwargs["height"] = height
        return fig.to_image(**kwargs)
    except Exception as e:
        st.error(f"Erro ao exportar PNG: {e}\nInstale kaleido: pip install kaleido")
        return None


def export_to_svg(fig: go.Figure) -> Optional[bytes]:
    """Export figure to SVG (vector)."""
    try:
        return fig.to_image(format="svg")
    except Exception as e:
        st.error(f"Erro ao exportar SVG: {e}\nInstale kaleido: pip install kaleido")
        return None


def export_to_pdf(fig: go.Figure) -> Optional[bytes]:
    """Export figure to PDF bytes."""
    try:
        return fig.to_image(format="pdf")
    except Exception as e:
        st.error(f"Erro ao exportar PDF: {e}\nInstale kaleido: pip install kaleido")
        return None


def render_export_panel(fig: go.Figure) -> None:
    """Render Streamlit export UI with all format options."""
    st.markdown("### 📥 Exportação")

    has_kaleido = try_import_kaleido()
    if not has_kaleido:
        st.warning(
            "⚠️ **kaleido** não encontrado. Apenas exportação HTML disponível.\n\n"
            "Para habilitar PNG/SVG/PDF, instale: `pip install kaleido`"
        )

    with st.expander("Opções de Exportação", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            export_scale = st.slider("Escala (PNG/PDF)", 1, 5, 3, key="export_scale",
                                     help="3 ≈ 300 DPI para figura 1000px")
            filename_base = st.text_input("Nome do arquivo", "sankey_diagram", key="export_filename")
        with c2:
            transparent_bg = st.checkbox("Fundo transparente (PNG)", False, key="transparent_bg")

        # HTML — always available
        html_bytes = export_to_html(fig, f"{filename_base}.html")
        st.download_button(
            label="⬇️ Baixar HTML Interativo",
            data=html_bytes,
            file_name=f"{filename_base}.html",
            mime="text/html",
            key="dl_html",
        )

        if has_kaleido:
            # Apply transparent background if requested
            export_fig = fig
            if transparent_bg:
                export_fig = go.Figure(fig)
                export_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

            c_png, c_svg, c_pdf = st.columns(3)

            with c_png:
                png_bytes = export_to_png(export_fig, scale=export_scale)
                if png_bytes:
                    st.download_button(
                        "⬇️ PNG",
                        data=png_bytes,
                        file_name=f"{filename_base}.png",
                        mime="image/png",
                        key="dl_png",
                    )

            with c_svg:
                svg_bytes = export_to_svg(export_fig)
                if svg_bytes:
                    st.download_button(
                        "⬇️ SVG (vetorial)",
                        data=svg_bytes,
                        file_name=f"{filename_base}.svg",
                        mime="image/svg+xml",
                        key="dl_svg",
                    )

            with c_pdf:
                pdf_bytes = export_to_pdf(export_fig)
                if pdf_bytes:
                    st.download_button(
                        "⬇️ PDF",
                        data=pdf_bytes,
                        file_name=f"{filename_base}.pdf",
                        mime="application/pdf",
                        key="dl_pdf",
                    )
