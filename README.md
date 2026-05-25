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

u, se preferir, crie um arquivo requirements.txt:
text

streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0

E instale com:
bash

pip install -r requirements.txt

3. Executar o aplicativo
bash

streamlit run app.py

O navegador abrirá automaticamente em http://localhost:8501.
📁 Estrutura do Projeto (modular)
text

sankeypro/
├── app.py                        # Ponto de entrada – interface principal
├── utils/
│   └── dataframe_parser.py       # Leitura, detecção de tipos, agregação e construção dos dados do Sankey
├── components/
│   ├── sankey_builder.py         # Cria o gráfico Plotly (trace Sankey)
│   ├── layout_manager.py         # Posicionamento automático ou manual dos nós
│   ├── style_manager.py          # Paletas de cores, fontes, configurações visuais
│   └── export_manager.py         # Botões de download (PNG, SVG, PDF, HTML)
└── README.md

🧠 Descrição das Funções (do código)
Função / Módulo	O que faz
load_dataframe()	Lê CSV/Excel, trata encoding e retorna um DataFrame pandas.
detect_categorical_columns()	Identifica colunas do tipo object, category ou boolean.
detect_numeric_columns()	Identifica colunas numéricas (int, float).
build_sankey_data()	Agrupa os dados conforme os níveis e a coluna de valor, aplica agregação, ordena nós, remove fluxos zero, gera dicionário com labels, sources, targets, values, totais por nó e total geral.
build_sankey_figure()	Constrói o objeto go.Sankey do Plotly com todas as opções de estilo (cores, opacidade, espessura, fonte, tooltips, título, margens, layout).
auto_layout()	Gera posições X e Y para os nós – distribuição uniforme por nível e, opcionalmente, posicionamento vertical ponderado pelo valor.
render_position_editor()	Cria sliders na interface para o usuário ajustar manualmente as coordenadas de cada nó.
build_full_config()	Lê todas as configurações de estilo das abas (paleta, fonte, cores, opacidade etc.) e retorna um dicionário.
render_export_panel()	Exibe botões para exportar o gráfico atual nos formatos PNG, SVG, PDF e HTML (usando a funcionalidade nativa do Plotly e plotly.io).
📊 Exemplo de Uso (Dataset incluso)

O programa fornece um dataset de exemplo ecológico com:

    Colunas de nível: Bacia → Espécie → Sexo

    Coluna de valor: Abundância

    Agregação padrão: soma

Basta clicar em "🧪 Usar Dataset de Exemplo" na barra lateral para testar todas as funcionalidades imediatamente.
🎛️ Personalização Técnica
Adicionar nova paleta de cores

Edite style_manager.py – adicione uma entrada ao dicionário COLOR_PALETTES seguindo o padrão:
python

"MinhaPaleta": ["#FF0000", "#00FF00", "#0000FF"]

Alterar o tipo de agregação padrão

Em app.py, na função sidebar_column_selection(), mude o parâmetro default do selectbox de "sum" para outra opção ("mean", "count", etc.).
Modificar o formato dos tooltips

No build_sankey_figure(), o parâmetro label_format aceita:

    "name_value" → "Nó: 150"

    "name" → somente o nome

    "value" → somente o valor

    "name_value_pct" → "Nó: 150 (12.5%)"
