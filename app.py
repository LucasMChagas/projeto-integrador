import streamlit as st
import hashlib
from pathlib import Path
import pandas as pd
from datetime import datetime
import json

# Configuração da página
st.set_page_config(
    page_title="Marketplace Pricing System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos do backend
from backend.auth import AuthManager
from backend.database import DatabaseManager
from backend.utils import apply_custom_theme

# Aplicar tema dark customizado
apply_custom_theme()

# Inicializar gerenciadores
auth_manager = AuthManager()
db_manager = DatabaseManager()

# Inicializar session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_hash = None
    st.session_state.user_name = None

def main():
    """Função principal da aplicação"""
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    """Página de login/registro"""
    
    st.markdown("""
        <div style='text-align: center; padding: 50px 0;'>
            <h1 style='color: #FF4B4B;'>💰 Marketplace Pricing System</h1>
            <p style='color: #808495;'>Sistema de Precificação para Marketplaces</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Cadastro"])
        
        with tab1:
            show_login_form()
        
        with tab2:
            show_register_form()

def show_login_form():
    """Formulário de login"""
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="seu@email.com")
        password = st.text_input("🔒 Senha", type="password", placeholder="******")
        submit = st.form_submit_button("Entrar", use_container_width=True, type="primary")
        
        if submit:
            if email and password:
                success, user_data = auth_manager.login(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_hash = user_data['hash']
                    st.session_state.user_name = user_data.get('name', email.split('@')[0])
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Email ou senha incorretos!")
            else:
                st.warning("⚠️ Por favor, preencha todos os campos!")

def show_register_form():
    """Formulário de cadastro"""
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 Nome completo", placeholder="João Silva")
            email = st.text_input("📧 Email", placeholder="seu@email.com")
        
        with col2:
            password = st.text_input("🔒 Senha", type="password", placeholder="Mínimo 6 caracteres")
            confirm_password = st.text_input("🔒 Confirmar senha", type="password", placeholder="Digite novamente")
        
        terms = st.checkbox("Li e aceito os termos de uso")
        submit = st.form_submit_button("Criar conta", use_container_width=True, type="primary")
        
        if submit:
            if not all([name, email, password, confirm_password]):
                st.warning("⚠️ Por favor, preencha todos os campos!")
            elif len(password) < 6:
                st.error("❌ A senha deve ter no mínimo 6 caracteres!")
            elif password != confirm_password:
                st.error("❌ As senhas não coincidem!")
            elif not terms:
                st.warning("⚠️ Você precisa aceitar os termos de uso!")
            else:
                success, message = auth_manager.register(email, password, name)
                if success:
                    st.success("✅ Conta criada com sucesso! Faça login para continuar.")
                else:
                    st.error(f"❌ {message}")

def show_main_app():
    """Aplicação principal após login"""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align: center; padding: 20px 0;'>
                <h3 style='color: #FF4B4B;'>💰 MP System</h3>
                <p style='color: #808495; font-size: 14px;'>Olá, {st.session_state.user_name}!</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Menu de navegação
        page = st.selectbox(
            "Navegação",
            options=[
                "🏠 Dashboard",
                "📦 Produtos",
                "🛒 Plataformas",
                "💰 Calculadora",
                "📊 Relatórios"
            ],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.user_hash = None
            st.session_state.user_name = None
            st.rerun()
    
    # Conteúdo principal baseado na página selecionada
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📦 Produtos":
        from pages.products import show_products_page
        show_products_page(st.session_state.user_hash)
    elif page == "🛒 Plataformas":
        from pages.platforms import show_platforms_page
        show_platforms_page(st.session_state.user_hash)
    elif page == "💰 Calculadora":
        from pages.calculator import show_calculator_page
        show_calculator_page(st.session_state.user_hash)
    elif page == "📊 Relatórios":
        from pages.reports import show_reports_page
        show_reports_page(st.session_state.user_hash)

def show_dashboard():
    """Dashboard principal"""
    
    st.title("🏠 Dashboard")
    st.markdown("---")
    
    # Inicializar gerenciador de banco
    db = DatabaseManager()
    user_hash = st.session_state.user_hash
    
    # Obter dados
    produtos = db.get_produtos(user_hash)
    plataformas = db.get_plataformas(user_hash)
    taxas = db.get_taxas_plataforma(user_hash)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_produtos = len(produtos) if not produtos.empty else 0
        st.metric(
            label="Total de Produtos",
            value=str(total_produtos),
            delta=f"{total_produtos} cadastrados"
        )
    
    with col2:
        total_plataformas = len(plataformas) if not plataformas.empty else 0
        plataformas_ativas = len(plataformas[plataformas['ativa'] == True]) if not plataformas.empty else 0
        st.metric(
            label="Plataformas Ativas",
            value=str(plataformas_ativas),
            delta=f"{total_plataformas} total"
        )
    
    with col3:
        if not produtos.empty and 'margem_liquida' in produtos.columns:
            margem_media = produtos['margem_liquida'].mean()
            margem_str = f"{margem_media:.1f}%" if not pd.isna(margem_media) else "0%"
        else:
            margem_str = "0%"
        st.metric(
            label="Margem Média",
            value=margem_str,
            delta="Calculada"
        )
    
    with col4:
        from datetime import datetime
        st.metric(
            label="Última Atualização",
            value="Hoje",
            delta=datetime.now().strftime("%H:%M")
        )
    
    st.markdown("---")
    
    # Área de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Produtos por Plataforma")
        if not produtos.empty and not plataformas.empty:
            # Criar gráfico de produtos por plataforma
            produtos_por_plat = produtos.groupby('plataforma').size() if 'plataforma' in produtos.columns else pd.Series()
            if not produtos_por_plat.empty:
                import plotly.graph_objects as go
                
                # Cores variadas para cada barra
                cores_barras = ['#2196F3', '#4CAF50', '#9C27B0', '#FF9800', '#00BCD4', '#E91E63', '#FFC107', '#795548']
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=produtos_por_plat.index,
                        y=produtos_por_plat.values,
                        marker_color=cores_barras[:len(produtos_por_plat)]
                    )
                ])
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#0E1117',
                    plot_bgcolor='#262730',
                    font=dict(color='#FAFAFA'),
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Cadastre produtos e associe às plataformas")
        else:
            st.info("Cadastre produtos e plataformas para visualizar")
    
    with col2:
        st.subheader("💹 Distribuição de Taxas")
        if not taxas.empty and not plataformas.empty:
            # Criar gráfico de taxas por plataforma
            taxas_por_plat = taxas.groupby('plataforma_id').size()
            plat_names = []
            for plat_id in taxas_por_plat.index:
                plat_name = plataformas[plataformas['id'] == plat_id]['nome'].values
                if len(plat_name) > 0:
                    plat_names.append(plat_name[0])
                else:
                    plat_names.append(f"Plataforma {plat_id}")
            
            if plat_names:
                import plotly.graph_objects as go
                cores_variadas = ['#2196F3', '#4CAF50', '#9C27B0', '#FF9800', '#00BCD4', '#E91E63']
                fig = go.Figure(data=[
                    go.Pie(
                        labels=plat_names,
                        values=taxas_por_plat.values,
                        hole=0.4,
                        marker=dict(colors=cores_variadas[:len(plat_names)]),
                        textfont=dict(color='#FAFAFA')
                    )
                ])
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#0E1117',
                    plot_bgcolor='#262730',
                    font=dict(color='#FAFAFA'),
                    margin=dict(l=0, r=0, t=30, b=0),
                    legend=dict(
                        font=dict(color='#FAFAFA')
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Configure taxas nas plataformas")
        else:
            st.info("Configure taxas nas plataformas para visualizar")
    
    # Seção de avisos e dicas
    st.markdown("---")
    st.subheader("💡 Dicas Rápidas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if total_plataformas == 0:
            st.warning("📦 Cadastre suas plataformas de venda")
        elif plataformas_ativas == 0:
            st.warning("⚠️ Ative pelo menos uma plataforma")
        else:
            st.success(f"✅ {plataformas_ativas} plataforma(s) ativa(s)")
    
    with col2:
        total_taxas = len(taxas) if not taxas.empty else 0
        if total_taxas == 0:
            st.warning("💰 Configure as taxas das plataformas")
        else:
            st.success(f"✅ {total_taxas} taxa(s) configurada(s)")
    
    with col3:
        if total_produtos == 0:
            st.warning("📦 Adicione seus produtos")
        else:
            st.success(f"✅ {total_produtos} produto(s) cadastrado(s)")

if __name__ == "__main__":
    main()