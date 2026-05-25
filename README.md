# SankeyPro 🌊

**Gerador Avançado e Interativo de Diagramas de Sankey**  
*Streamlit + Plotly – para análises científicas e de negócios*

![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)

---

## 📖 Sobre o Programa

O **SankeyPro** é uma aplicação web desenvolvida com **Streamlit** e **Plotly** que permite criar diagramas de Sankey dinâmicos, altamente customizáveis e prontos para uso científico ou corporativo.

A ferramenta transforma dados tabulares (CSV/Excel) em fluxos visuais entre categorias organizadas em níveis – por exemplo:

- **Ecologia**: Bacia hidrográfica → Espécie → Sexo (com abundância ou biomassa)
- **Energia**: Fonte → Processo → Consumo final (valores em MWh)
- **Finanças**: Categoria → Subcategoria → Produto (valores monetários)

O usuário pode controlar cada aspecto da visualização: cores, opacidade, ordenação dos nós, posicionamento manual, filtros interativos, agregação dos dados (soma, média, contagem etc.) e exportação em múltiplos formatos (PNG, SVG, PDF, HTML).

---

## ✨ Funcionalidades Principais

| Módulo | Descrição |
|--------|------------|
| **Carregamento de dados** | CSV, Excel (xlsx, xls) ou dataset de exemplo integrado |
| **Seleção de níveis** | Quantas colunas categóricas desejar – a ordem define o fluxo |
| **Coluna de valores** | Qualquer coluna numérica (abundância, receita, frequência etc.) |
| **Agregação flexível** | Soma, média, contagem, máximo, mínimo |
| **Filtros dinâmicos** | Incluir/excluir categorias de cada nível em tempo real |
| **Ordenação de nós** | Por valor, ordem alfabética ou personalizada (manual) |
| **Posicionamento manual** | Controle individual das coordenadas X e Y de cada nó |
| **Estilo completo** | 10 paletas de cores, opacidade de nós e links, espessura, fontes (12 famílias), cores de fundo, bordas |
| **Tooltips científicos** | Mostram valor, percentual do total, rank e nome da métrica |
| **Exportação profissional** | PNG (alta resolução), SVG, PDF, HTML interativo |

---

## 🚀 Como Executar (Local)

### 1. Pré‑requisitos
- Python 3.8 ou superior
- pip

### 2. Instalar dependências

```bash
pip install streamlit pandas numpy plotly openpyxl

**Ou, se preferir, crie um arquivo requirements.txt:**

streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0

**E instale com:**
pip install -r requirements.txt
