"""
Módulo de Gestão de Produtos
Interface para gerenciar produtos e suas precificações
"""

import streamlit as st
import pandas as pd
from backend.database import DatabaseManager
from backend.utils import (
    format_currency,
    format_percentage,
    get_sample_products_template,
    export_to_excel,
    calculate_price
)
import io

def show_products_page(user_hash: str):
    """Página principal de gestão de produtos"""
    
    st.title("📦 Gestão de Produtos")
    st.markdown("---")
    
    # Inicializar gerenciador de banco
    db = DatabaseManager()
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Lista de Produtos",
        "➕ Novo Produto", 
        "📥 Importar",
        "📤 Exportar",
        "🔧 Campos Personalizados"
    ])
    
    with tab1:
        show_products_list(db, user_hash)
    
    with tab2:
        add_new_product(db, user_hash)
    
    with tab3:
        import_products(db, user_hash)
    
    with tab4:
        export_products(db, user_hash)
    
    with tab5:
        manage_custom_fields(db, user_hash)

def show_products_list(db: DatabaseManager, user_hash: str):
    """Mostra lista de produtos cadastrados"""
    
    produtos = db.get_produtos(user_hash)
    plataformas = db.get_plataformas(user_hash)
    
    if produtos.empty:
        st.info("📭 Nenhum produto cadastrado ainda. Clique em 'Novo Produto' para começar!")
        return
    
    # Estatísticas rápidas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(produtos)
        st.metric("Total de Produtos", total)
    
    with col2:
        if 'custo' in produtos.columns:
            custo_total = produtos['custo'].sum()
            st.metric("Custo Total", format_currency(custo_total))
        else:
            st.metric("Custo Total", "R$ 0,00")
    
    with col3:
        if 'margem_liquida' in produtos.columns and not produtos['margem_liquida'].isna().all():
            margem_media = produtos['margem_liquida'].mean()
            st.metric("Margem Média", format_percentage(margem_media))
        else:
            st.metric("Margem Média", "0%")
    
    with col4:
        categorias = produtos['categoria'].nunique() if 'categoria' in produtos.columns else 0
        st.metric("Categorias", categorias)
    
    st.markdown("---")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search = st.text_input("🔍 Buscar produto", placeholder="Nome ou SKU...")
    
    with col2:
        if 'categoria' in produtos.columns:
            categorias = ['Todas'] + produtos['categoria'].dropna().unique().tolist()
            categoria_filter = st.selectbox("📁 Categoria", categorias)
        else:
            categoria_filter = 'Todas'
    
    with col3:
        if 'plataforma' in produtos.columns and not plataformas.empty:
            plats = ['Todas'] + plataformas['nome'].tolist()
            plataforma_filter = st.selectbox("🛒 Plataforma", plats)
        else:
            plataforma_filter = 'Todas'
    
    # Aplicar filtros
    produtos_filtrados = produtos.copy()
    
    if search:
        mask = (
            produtos_filtrados['nome'].str.contains(search, case=False, na=False) |
            produtos_filtrados['sku'].str.contains(search, case=False, na=False)
        )
        produtos_filtrados = produtos_filtrados[mask]
    
    if categoria_filter != 'Todas':
        produtos_filtrados = produtos_filtrados[produtos_filtrados['categoria'] == categoria_filter]
    
    if plataforma_filter != 'Todas':
        produtos_filtrados = produtos_filtrados[produtos_filtrados['plataforma'] == plataforma_filter]
    
    # Mostrar produtos
    st.markdown(f"### 📦 Produtos ({len(produtos_filtrados)} encontrados)")
    
    for idx, produto in produtos_filtrados.iterrows():
        with st.expander(f"**{produto['nome']}** - SKU: {produto['sku']}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write("**Informações Básicas:**")
                st.write(f"• **SKU:** {produto['sku']}")
                st.write(f"• **Categoria:** {produto.get('categoria', 'N/A')}")
                st.write(f"• **Descrição:** {produto.get('descricao', 'N/A')}")
                
                if 'peso' in produto and pd.notna(produto['peso']):
                    st.write(f"• **Peso:** {produto['peso']}")
                if 'dimensoes' in produto and pd.notna(produto['dimensoes']):
                    st.write(f"• **Dimensões:** {produto['dimensoes']}")
            
            with col2:
                st.write("**Informações Financeiras:**")
                st.write(f"• **Custo:** {format_currency(produto.get('custo', 0))}")
                st.write(f"• **Frete:** {format_currency(produto.get('frete', 0))}")
                
                if 'preco_calculado' in produto and pd.notna(produto['preco_calculado']):
                    st.write(f"• **Preço Sugerido:** {format_currency(produto['preco_calculado'])}")
                if 'margem_liquida' in produto and pd.notna(produto['margem_liquida']):
                    st.write(f"• **Margem:** {format_percentage(produto['margem_liquida'])}")
                
                if 'plataforma' in produto and pd.notna(produto['plataforma']):
                    st.write(f"• **Plataforma:** {produto['plataforma']}")
            
            with col3:
                st.write("**Ações:**")
                
                # Editar
                if st.button("✏️ Editar", key=f"edit_{produto['id']}"):
                    st.session_state[f'editing_product_{produto["id"]}'] = True
                    st.rerun()
                
                # Calcular preço
                if st.button("💰 Calcular", key=f"calc_{produto['id']}"):
                    st.session_state['calc_product_id'] = produto['id']
                    st.session_state['show_calculator'] = True
                    st.rerun()
                
                # Excluir com confirmação adequada
                if st.button("🗑️ Excluir", key=f"delete_{produto['id']}"):
                    st.session_state[f'confirm_delete_{produto["id"]}'] = True
                    st.rerun()
                
                # Mostrar confirmação se necessário
                if st.session_state.get(f'confirm_delete_{produto["id"]}', False):
                    st.warning(f"⚠️ Confirmar exclusão de **{produto['nome']}**?")
                    col_yes, col_no = st.columns(2)
                    
                    with col_yes:
                        if st.button("✅ Sim", key=f"confirm_yes_{produto['id']}"):
                            success, msg = db.delete_produto(user_hash, produto['id'])
                            if success:
                                st.success(msg)
                                # Limpar estado de confirmação
                                if f'confirm_delete_{produto["id"]}' in st.session_state:
                                    del st.session_state[f'confirm_delete_{produto["id"]}']
                                st.rerun()
                            else:
                                st.error(msg)
                    
                    with col_no:
                        if st.button("❌ Não", key=f"confirm_no_{produto['id']}"):
                            # Limpar estado de confirmação
                            if f'confirm_delete_{produto["id"]}' in st.session_state:
                                del st.session_state[f'confirm_delete_{produto["id"]}']
                            st.rerun()
            
            # Mostrar campos customizados se existirem
            custom_fields = db.get_custom_fields(user_hash, 'produtos')
            if custom_fields:
                st.write("**Campos Personalizados:**")
                for field in custom_fields:
                    if field in produto and pd.notna(produto[field]):
                        st.write(f"• **{field}:** {produto[field]}")
            
            # Modo de edição
            if st.session_state.get(f'editing_product_{produto["id"]}', False):
                st.markdown("---")
                edit_product_form(db, user_hash, produto)

def edit_product_form(db: DatabaseManager, user_hash: str, produto):
    """Formulário de edição de produto inline"""
    
    with st.form(f"edit_product_form_{produto['id']}"):
        st.write("### ✏️ Editar Produto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome", value=produto['nome'])
            sku = st.text_input("SKU", value=produto['sku'])
            categoria = st.text_input("Categoria", value=produto.get('categoria', ''))
            descricao = st.text_area("Descrição", value=produto.get('descricao', ''))
        
        with col2:
            custo = st.number_input("Custo (R$)", value=float(produto.get('custo', 0)), min_value=0.0, step=0.01)
            frete = st.number_input("Frete (R$)", value=float(produto.get('frete', 0)), min_value=0.0, step=0.01)
            peso = st.text_input("Peso", value=produto.get('peso', ''))
            dimensoes = st.text_input("Dimensões", value=produto.get('dimensoes', ''))
        
        # Campos customizados
        custom_fields = db.get_custom_fields(user_hash, 'produtos')
        custom_values = {}
        if custom_fields:
            st.write("**Campos Personalizados:**")
            for field in custom_fields:
                custom_values[field] = st.text_input(
                    field,
                    value=str(produto.get(field, '')) if field in produto else ''
                )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Salvar", type="primary"):
                update_data = {
                    'nome': nome,
                    'sku': sku,
                    'categoria': categoria,
                    'descricao': descricao,
                    'custo': custo,
                    'frete': frete,
                    'peso': peso,
                    'dimensoes': dimensoes,
                    **custom_values
                }
                
                success, msg = db.update_produto(user_hash, produto['id'], update_data)
                if success:
                    st.success(msg)
                    del st.session_state[f'editing_product_{produto["id"]}']
                    st.rerun()
                else:
                    st.error(msg)
        
        with col2:
            if st.form_submit_button("❌ Cancelar"):
                del st.session_state[f'editing_product_{produto["id"]}']
                st.rerun()

def add_new_product(db: DatabaseManager, user_hash: str):
    """Formulário para adicionar novo produto"""
    
    st.subheader("➕ Adicionar Novo Produto")
    
    plataformas = db.get_plataformas(user_hash)
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Informações Básicas")
            nome = st.text_input("Nome do Produto *", placeholder="Ex: Camiseta Básica")
            sku = st.text_input("SKU (Código Único) *", placeholder="Ex: CAM-001")
            categoria = st.text_input("Categoria", placeholder="Ex: Vestuário")
            descricao = st.text_area("Descrição", placeholder="Descrição detalhada do produto...")
        
        with col2:
            st.markdown("### Informações Financeiras")
            custo = st.number_input("Custo do Produto (R$) *", min_value=0.0, step=0.01, help="Valor de custo do produto")
            frete = st.number_input("Frete (R$)", min_value=0.0, step=0.01, value=0.0, help="Custo de frete/envio")
            
            st.markdown("### Informações Adicionais")
            peso = st.text_input("Peso", placeholder="Ex: 0.5kg")
            dimensoes = st.text_input("Dimensões", placeholder="Ex: 20x15x10 cm")
        
        # Plataforma
        if not plataformas.empty:
            st.markdown("### Plataforma")
            plataforma = st.selectbox(
                "Selecione a plataforma (opcional)",
                options=['Nenhuma'] + plataformas['nome'].tolist()
            )
        else:
            plataforma = 'Nenhuma'
            st.info("💡 Cadastre plataformas para associar produtos a elas")
        
        # Campos customizados
        custom_fields = db.get_custom_fields(user_hash, 'produtos')
        custom_values = {}
        if custom_fields:
            st.markdown("### Campos Personalizados")
            for field in custom_fields:
                custom_values[field] = st.text_input(field, placeholder=f"Digite {field}...")
        
        st.markdown("---")
        
        # Botão de submit
        submitted = st.form_submit_button("Adicionar Produto", type="primary", use_container_width=True)
        
        if submitted:
            if not nome or not sku or custo <= 0:
                st.error("❌ Preencha todos os campos obrigatórios!")
            else:
                produto_data = {
                    'nome': nome,
                    'sku': sku,
                    'categoria': categoria if categoria else 'Geral',
                    'descricao': descricao,
                    'custo': custo,
                    'frete': frete,
                    'peso': peso,
                    'dimensoes': dimensoes,
                    'plataforma': plataforma if plataforma != 'Nenhuma' else None,
                    **custom_values
                }
                
                success, msg = db.add_produto(user_hash, produto_data)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

def import_products(db: DatabaseManager, user_hash: str):
    """Interface para importar produtos via Excel"""
    
    st.subheader("📥 Importar Produtos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Como funciona:")
        st.write("""
        1. Baixe o modelo de planilha
        2. Preencha com seus produtos
        3. Faça upload do arquivo preenchido
        4. Revise e confirme a importação
        """)
        
        # Download do template
        template_df = get_sample_products_template()
        
        # Adicionar campos customizados ao template
        custom_fields = db.get_custom_fields(user_hash, 'produtos')
        for field in custom_fields:
            template_df[field] = ''
        
        # Converter para Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Produtos')
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Baixar Modelo de Planilha",
            data=excel_data,
            file_name="modelo_produtos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        st.markdown("### Upload de Arquivo")
        
        uploaded_file = st.file_uploader(
            "Selecione o arquivo Excel",
            type=['xlsx', 'xls'],
            help="Faça upload da planilha preenchida com seus produtos"
        )
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Arquivo carregado! {len(df)} produtos encontrados.")
                
                # Preview dos dados
                st.write("**Preview dos dados:**")
                st.dataframe(df.head())
                
                # Validação
                required_cols = ['sku', 'nome', 'custo']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Colunas obrigatórias faltando: {', '.join(missing_cols)}")
                else:
                    if st.button("✅ Confirmar Importação", type="primary", use_container_width=True):
                        success, msg = db.import_produtos_excel(user_hash, uploaded_file.getvalue())
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                            
            except Exception as e:
                st.error(f"❌ Erro ao ler arquivo: {str(e)}")

def export_products(db: DatabaseManager, user_hash: str):
    """Interface para exportar produtos"""
    
    st.subheader("📤 Exportar Produtos")
    
    produtos = db.get_produtos(user_hash)
    
    if produtos.empty:
        st.warning("⚠️ Nenhum produto para exportar!")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total de Produtos", len(produtos))
        st.write("**Informações que serão exportadas:**")
        st.write("• Todos os produtos cadastrados")
        st.write("• Informações completas")
        st.write("• Campos personalizados")
        st.write("• Dados de precificação")
    
    with col2:
        # Opções de exportação
        st.write("**Formato de exportação:**")
        
        # Exportar Excel
        excel_data = db.export_produtos_excel(user_hash)
        
        if excel_data:
            st.download_button(
                label="📥 Baixar Excel Completo",
                data=excel_data,
                file_name=f"produtos_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # Exportar CSV
        csv = produtos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name=f"produtos_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def manage_custom_fields(db: DatabaseManager, user_hash: str):
    """Gerenciar campos personalizados"""
    
    st.subheader("🔧 Campos Personalizados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Campos Atuais")
        
        # Campos padrão
        st.write("**Campos Padrão (não removíveis):**")
        campos_padrao = ['id', 'sku', 'nome', 'descricao', 'custo', 'frete', 
                        'categoria', 'peso', 'dimensoes', 'plataforma']
        for campo in campos_padrao:
            st.write(f"• {campo}")
        
        # Campos customizados
        custom_fields = db.get_custom_fields(user_hash, 'produtos')
        
        if custom_fields:
            st.write("**Campos Personalizados:**")
            for field in custom_fields:
                col_field, col_action = st.columns([3, 1])
                with col_field:
                    st.write(f"• {field}")
                with col_action:
                    if st.button("🗑️", key=f"remove_field_{field}", help=f"Remover {field}"):
                        # Implementar remoção de campo
                        st.warning("Função de remoção será implementada em breve")
        else:
            st.info("Nenhum campo personalizado criado ainda")
    
    with col2:
        st.markdown("### Adicionar Novo Campo")
        
        with st.form("add_custom_field"):
            nome_campo = st.text_input(
                "Nome do Campo",
                placeholder="Ex: cor, tamanho, fornecedor",
                help="Use apenas letras, números e underscore"
            )
            
            tipo_campo = st.selectbox(
                "Tipo do Campo",
                options=['text', 'number', 'date'],
                format_func=lambda x: {
                    'text': '📝 Texto',
                    'number': '🔢 Número',
                    'date': '📅 Data'
                }.get(x, x)
            )
            
            st.info("""
            💡 **Nota:** Campos personalizados serão adicionados a todos os produtos.
            Produtos existentes terão valor vazio inicialmente.
            """)
            
            submitted = st.form_submit_button("Adicionar Campo", type="primary", use_container_width=True)
            
            if submitted:
                if not nome_campo:
                    st.error("❌ Digite o nome do campo!")
                elif ' ' in nome_campo:
                    st.error("❌ O nome do campo não pode conter espaços! Use underscore (_)")
                elif nome_campo in campos_padrao:
                    st.error("❌ Este nome já é usado por um campo padrão!")
                elif nome_campo in custom_fields:
                    st.error("❌ Este campo já existe!")
                else:
                    success, msg = db.add_custom_field(user_hash, 'produtos', nome_campo, tipo_campo)
                    if success:
                        st.success(f"✅ Campo '{nome_campo}' adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

# Calculadora de preços (será chamada quando necessário)
def show_price_calculator(db: DatabaseManager, user_hash: str, produto_id: int):
    """Mostra calculadora de preços para um produto específico"""
    
    # Esta função será integrada com o módulo de calculadora
    # Por enquanto, apenas um placeholder
    st.info("💰 Calculadora será implementada no próximo módulo")