"""
Módulo de Utilitários
Funções auxiliares e configurações gerais
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Any

def apply_custom_theme():
    """Aplica tema dark customizado ao Streamlit"""
    st.markdown("""
        <style>
        /* Tema Dark Customizado com melhor legibilidade */
        
        /* Background e texto principal */
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        
        /* Força todos os textos para branco */
        .stMarkdown, .stText, p, span, label {
            color: #FAFAFA !important;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #FAFAFA !important;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #1A1D24;
            border-right: 1px solid #262730;
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: #FAFAFA !important;
        }
        
        section[data-testid="stSidebar"] label {
            color: #FAFAFA !important;
        }
        
        /* Selectbox - Corrigindo fundo branco */
        [data-baseweb="select"] {
            background-color: #262730 !important;
        }
        
        [data-baseweb="select"] > div {
            background-color: #262730 !important;
            color: #FAFAFA !important;
        }
        
        [data-baseweb="select"] [data-baseweb="select-placeholder"] {
            color: #B0B7C3 !important;
        }
        
        /* Dropdown menu */
        [data-baseweb="menu"] {
            background-color: #262730 !important;
        }
        
        [data-baseweb="menu-item"] {
            background-color: #262730 !important;
            color: #FAFAFA !important;
        }
        
        [data-baseweb="menu-item"]:hover {
            background-color: #363842 !important;
        }
        
        /* Popover e Tooltips */
        [data-baseweb="popover"] {
            background-color: #262730 !important;
        }
        
        [data-baseweb="popover-body"] {
            background-color: #262730 !important;
            color: #FAFAFA !important;
        }
        
        /* Radio buttons e Checkboxes */
        .stRadio > div {
            background-color: transparent !important;
        }
        
        .stRadio label {
            color: #FAFAFA !important;
        }
        
        .stCheckbox label {
            color: #FAFAFA !important;
        }
        
        /* Expander - Corrigindo contraste */
        .streamlit-expanderHeader {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border-radius: 0.5rem;
        }
        
        /* AJUSTE ESPECÍFICO PARA FORÇAR TEXTO BRANCO NO EXPANDER */
        .streamlit-expanderHeader p,
        .streamlit-expanderHeader span,
        .streamlit-expanderHeader strong {
            color: #FAFAFA !important;
        }
        
        [data-testid="stExpander"] summary * {
            color: #FAFAFA !important;
        }
        
        .streamlit-expanderContent {
            background-color: #1A1D24 !important;
            border: 1px solid #363842;
            color: #FAFAFA !important;
        }
        
        /* Cards e containers */
        .element-container {
            background-color: transparent;
            color: #FAFAFA;
        }
        
        div[data-testid="metric-container"] {
            background-color: #262730;
            border: 1px solid #363842;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        
        /* Botões */
        .stButton > button {
            background-color: #FF4B4B;
            color: white !important;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            border-radius: 0.5rem;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            background-color: #FF6B6B;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border: 1px solid #363842 !important;
        }
        
        .stNumberInput > div > div > input {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border: 1px solid #363842 !important;
        }
        
        .stTextArea > div > div > textarea {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border: 1px solid #363842 !important;
        }
        
        /* Labels dos inputs */
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label,
        .stNumberInput label,
        .stCheckbox label,
        .stRadio label {
            color: #FAFAFA !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1A1D24 !important;
            border-radius: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #B0B7C3 !important;
            background-color: transparent !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #262730 !important;
            color: #FF4B4B !important;
        }
        
        /* DataFrames e Tabelas */
        .dataframe {
            background-color: #262730 !important;
            color: #FAFAFA !important;
        }
        
        .dataframe th {
            background-color: #1A1D24 !important;
            color: #FAFAFA !important;
        }
        
        .dataframe td {
            color: #FAFAFA !important;
        }
        
        /* Métricas */
        [data-testid="metric-container"] [data-testid="metric-label"] {
            color: #B0B7C3 !important;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            color: #FAFAFA !important;
            font-size: 1.875rem;
            font-weight: 600;
        }
        
        [data-testid="metric-container"] [data-testid="metric-delta"] {
            font-size: 0.875rem;
            color: inherit !important;
        }
        
        /* Dividers */
        hr {
            border-color: #363842;
        }
        
        /* Alertas e notificações */
        .stAlert {
            background-color: #262730 !important;
            border: 1px solid;
            border-radius: 0.5rem;
            color: #FAFAFA !important;
        }
        
        .stAlert > div {
            color: #FAFAFA !important;
        }
        
        .stInfo {
            background-color: #1E3A5F !important;
            color: #FAFAFA !important;
        }
        
        .stSuccess {
            background-color: #1E5F3A !important;
            color: #FAFAFA !important;
        }
        
        .stWarning {
            background-color: #5F4B1E !important;
            color: #FAFAFA !important;
        }
        
        .stError {
            background-color: #5F1E1E !important;
            color: #FAFAFA !important;
        }
        
        div[data-baseweb="notification"] {
            background-color: #262730 !important;
            color: #FAFAFA !important;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1A1D24;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #363842;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #4A4D58;
        }
        
        /* Form submit button */
        .stForm [data-testid="stFormSubmitButton"] > button {
            background-color: #FF4B4B;
            color: white !important;
            width: 100%;
        }
        
        /* File uploader */
        .stFileUploader label {
            color: #FAFAFA !important;
        }
        
        section[data-testid="stFileUploadDropzone"] {
            background-color: #262730 !important;
            color: #B0B7C3 !important;
        }
        
        /* Modal/Dialog backgrounds */
        [data-baseweb="modal"] {
            background-color: #262730 !important;
        }
        
        [data-baseweb="modal-body"] {
            background-color: #262730 !important;
            color: #FAFAFA !important;
        }
        
        /* Sidebar selectbox específico */
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            background-color: #262730 !important;
            border: 1px solid #363842 !important;
        }
        
        /* Container principal dos forms */
        [data-testid="stForm"] {
            background-color: #1A1D24 !important;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #363842;
        }
        
        /* Garante que todo texto seja visível */
        .element-container span,
        .element-container div,
        .element-container p {
            color: #FAFAFA;
        }
        
        /* Input number spin buttons */
        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button {
            opacity: 0.5;
        }
        
        /* Placeholder text */
        input::placeholder,
        textarea::placeholder {
            color: #808495 !important;
        }
        
        /* Focus state dos inputs */
        input:focus,
        textarea:focus,
        select:focus {
            outline: 2px solid #FF4B4B !important;
            outline-offset: 2px;
        }
        </style>
    """, unsafe_allow_html=True)

def format_currency(value: float) -> str:
    """Formata valor para moeda brasileira"""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percentage(value: float) -> str:
    """Formata valor para percentual"""
    return f"{value:.1f}%"

def calculate_price(custo: float, frete: float, taxas: List[Dict], margem_desejada: float) -> Dict:
    """
    Calcula o preço final considerando todas as taxas
    
    Args:
        custo: Custo do produto
        frete: Valor do frete
        taxas: Lista de taxas a serem aplicadas
        margem_desejada: Margem de lucro desejada (0-1)
    
    Returns:
        Dict com preço sugerido, taxas totais e lucro líquido
    """
    custo_total = custo + frete
    
    # Processar taxas na ordem de prioridade
    taxas_sorted = sorted(taxas, key=lambda x: x.get('prioridade', 999))
    
    total_taxa_fixa = 0
    total_taxa_percentual = 0
    
    for taxa in taxas_sorted:
        if not taxa.get('ativa', True):
            continue
        
        # Avaliar condição se existir
        if taxa.get('condicao'):
            try:
                # Avaliar condição (implementar parser mais robusto em produção)
                if not eval_condition(taxa['condicao'], custo_total):
                    continue
            except:
                continue
        
        # Aplicar taxa
        if taxa['tipo_taxa'] == 'fixa':
            total_taxa_fixa += taxa['valor']
        elif taxa['tipo_taxa'] == 'percentual':
            total_taxa_percentual += taxa['valor'] / 100
    
    # Calcular preço final
    # Preço = (Custo + Taxa Fixa) / (1 - Margem - Taxa Percentual)
    denominador = 1 - margem_desejada - total_taxa_percentual
    
    if denominador <= 0:
        return {
            'erro': 'Margem + Taxas percentuais >= 100%. Impossível calcular.',
            'preco_sugerido': 0,
            'taxa_total': 0,
            'lucro_liquido': 0
        }
    
    preco_sugerido = (custo_total + total_taxa_fixa) / denominador
    taxa_total_valor = total_taxa_fixa + (preco_sugerido * total_taxa_percentual)
    lucro_liquido = preco_sugerido - custo_total - taxa_total_valor
    
    return {
        'preco_sugerido': round(preco_sugerido, 2),
        'custo_total': round(custo_total, 2),
        'taxa_total': round(taxa_total_valor, 2),
        'taxa_fixa': round(total_taxa_fixa, 2),
        'taxa_percentual': round(total_taxa_percentual * 100, 2),
        'lucro_liquido': round(lucro_liquido, 2),
        'margem_real': round((lucro_liquido / preco_sugerido) * 100, 2) if preco_sugerido > 0 else 0
    }

def eval_condition(condition: str, preco: float) -> bool:
    """
    Avalia uma condição simples para aplicação de taxa
    
    Exemplos de condições:
    - "preco > 100"
    - "preco <= 50"
    - "sempre" ou "true"
    """
    condition = condition.lower().strip()
    
    if condition in ['sempre', 'true', '1']:
        return True
    
    if condition in ['nunca', 'false', '0']:
        return False
    
    # Avaliar condições com preço
    try:
        # Substituir 'preco' pelo valor real
        condition = condition.replace('preco', str(preco))
        condition = condition.replace('valor', str(preco))
        
        # Avaliar expressão (cuidado em produção - usar parser seguro)
        return eval(condition)
    except:
        return True  # Em caso de erro, aplicar taxa por segurança

def create_dashboard_chart(df: pd.DataFrame, chart_type: str = 'bar') -> go.Figure:
    """Cria gráficos para o dashboard"""
    
    # Paleta de cores variadas
    cores_variadas = ['#2196F3', '#4CAF50', '#9C27B0', '#FF9800', '#00BCD4', '#E91E63', '#FFC107', '#795548']
    
    # Configurar tema dark para Plotly
    layout = go.Layout(
        template='plotly_dark',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font=dict(color='#FAFAFA'),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    if chart_type == 'bar' and not df.empty:
        fig = go.Figure(data=[
            go.Bar(
                x=df.index[:10],
                y=df.values[:10],
                marker_color='#2196F3'
            )
        ], layout=layout)
    
    elif chart_type == 'pie' and not df.empty:
        fig = go.Figure(data=[
            go.Pie(
                labels=df.index[:5],
                values=df.values[:5],
                hole=0.4,
                marker=dict(colors=cores_variadas[:len(df.index[:5])])
            )
        ], layout=layout)
    
    elif chart_type == 'line' and not df.empty:
        fig = go.Figure(data=[
            go.Scatter(
                x=df.index,
                y=df.values,
                mode='lines+markers',
                line=dict(color='#4CAF50', width=2),
                marker=dict(size=8, color='#4CAF50')
            )
        ], layout=layout)
    
    else:
        # Gráfico vazio
        fig = go.Figure(layout=layout)
        fig.add_annotation(
            text="Sem dados para exibir",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color='#808495')
        )
    
    return fig

def validate_email(email: str) -> bool:
    """Valida formato de email"""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def show_confirmation_dialog(message: str) -> bool:
    """Mostra diálogo de confirmação"""
    return st.button(f"⚠️ {message}", type="secondary")

def export_to_excel(dataframes: Dict[str, pd.DataFrame]) -> bytes:
    """
    Exporta múltiplos DataFrames para um arquivo Excel
    
    Args:
        dataframes: Dicionário com nome da aba e DataFrame
    
    Returns:
        Bytes do arquivo Excel
    """
    import io
    
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return buffer.getvalue()

def import_from_excel(file_data: bytes, expected_columns: List[str]) -> tuple:
    """
    Importa dados de um arquivo Excel
    
    Args:
        file_data: Bytes do arquivo
        expected_columns: Colunas esperadas
    
    Returns:
        tuple: (sucesso: bool, dados: DataFrame ou mensagem de erro)
    """
    try:
        import io
        df = pd.read_excel(io.BytesIO(file_data))
        
        # Validar colunas
        missing_cols = set(expected_columns) - set(df.columns)
        if missing_cols:
            return False, f"Colunas faltantes: {', '.join(missing_cols)}"
        
        return True, df
        
    except Exception as e:
        return False, f"Erro ao ler arquivo: {str(e)}"

def get_sample_products_template() -> pd.DataFrame:
    """Retorna template de exemplo para importação de produtos"""
    return pd.DataFrame({
        'sku': ['PROD001', 'PROD002', 'PROD003'],
        'nome': ['Produto Exemplo 1', 'Produto Exemplo 2', 'Produto Exemplo 3'],
        'descricao': ['Descrição do produto 1', 'Descrição do produto 2', 'Descrição do produto 3'],
        'custo': [50.00, 75.00, 100.00],
        'frete': [10.00, 15.00, 20.00],
        'categoria': ['Eletrônicos', 'Roupas', 'Acessórios'],
        'peso': ['0.5kg', '0.3kg', '0.2kg'],
        'dimensoes': ['10x10x5', '20x15x3', '5x5x2']
    })

def show_success_message(message: str, duration: int = 3):
    """Mostra mensagem de sucesso temporária"""
    placeholder = st.empty()
    placeholder.success(f"✅ {message}")
    import time
    time.sleep(duration)
    placeholder.empty()

def show_error_message(message: str, duration: int = 3):
    """Mostra mensagem de erro temporária"""
    placeholder = st.empty()
    placeholder.error(f"❌ {message}")
    import time
    time.sleep(duration)
    placeholder.empty()

def get_platform_suggestions() -> List[str]:
    """Retorna sugestões de plataformas comuns"""
    return [
        'Shopee',
        'Mercado Livre',
        'Amazon',
        'Magalu',
        'Americanas',
        'OLX',
        'Enjoei',
        'Elo7',
        'Instagram Shopping',
        'Facebook Marketplace'
    ]

def get_tax_type_options() -> Dict[str, str]:
    """Retorna tipos de taxa disponíveis"""
    return {
        'percentual': '📊 Percentual (%)',
        'fixa': '💵 Valor Fixo (R$)'
    }

def get_tax_suggestions() -> List[Dict]:
    """Retorna sugestões de taxas comuns"""
    return [
        {'nome': 'Comissão da Plataforma', 'tipo': 'percentual', 'descricao': 'Taxa básica cobrada pela plataforma'},
        {'nome': 'Taxa por Venda', 'tipo': 'fixa', 'descricao': 'Valor fixo cobrado por transação'},
        {'nome': 'Taxa de Anúncio Premium', 'tipo': 'percentual', 'descricao': 'Taxa adicional para anúncios em destaque'},
        {'nome': 'Taxa de Processamento', 'tipo': 'percentual', 'descricao': 'Taxa de processamento de pagamento'},
        {'nome': 'Frete Grátis', 'tipo': 'fixa', 'descricao': 'Custo do frete grátis oferecido'},
        {'nome': 'Desconto Nível Vendedor', 'tipo': 'percentual', 'descricao': 'Desconto baseado no nível do vendedor'}
    ]