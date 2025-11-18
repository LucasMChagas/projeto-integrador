"""
Módulo de Gestão de Plataformas
Interface para gerenciar plataformas e suas taxas dinâmicas
"""

import streamlit as st
import pandas as pd
from backend.database import DatabaseManager
from backend.utils import (
    format_currency, 
    format_percentage,
    get_platform_suggestions,
    get_tax_type_options,
    get_tax_suggestions
)

def show_platforms_page(user_hash: str):
    """Página principal de gestão de plataformas"""
    
    st.title("🛒 Gestão de Plataformas")
    st.markdown("---")
    
    # Inicializar gerenciador de banco
    db = DatabaseManager()
    
    # Tabs principais
    tab1, tab2, tab3 = st.tabs(["📋 Plataformas Cadastradas", "➕ Nova Plataforma", "💰 Configurar Taxas"])
    
    with tab1:
        show_platforms_list(db, user_hash)
    
    with tab2:
        add_new_platform(db, user_hash)
    
    with tab3:
        configure_taxes(db, user_hash)

def show_platforms_list(db: DatabaseManager, user_hash: str):
    """Mostra lista de plataformas cadastradas"""
    
    plataformas = db.get_plataformas(user_hash)
    
    if plataformas.empty:
        st.info("📭 Nenhuma plataforma cadastrada ainda. Clique em 'Nova Plataforma' para começar!")
        return
    
    # Estatísticas rápidas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = len(plataformas)
        st.metric("Total de Plataformas", total)
    
    with col2:
        ativas = len(plataformas[plataformas['ativa'] == True])
        st.metric("Plataformas Ativas", ativas)
    
    with col3:
        # Contar taxas configuradas
        todas_taxas = db.get_taxas_plataforma(user_hash)
        total_taxas = len(todas_taxas) if not todas_taxas.empty else 0
        st.metric("Taxas Configuradas", total_taxas)
    
    st.markdown("---")
    
    # Lista de plataformas
    for idx, plataforma in plataformas.iterrows():
        with st.expander(f"**{plataforma['nome']}** {'✅' if plataforma['ativa'] else '❌'}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**ID:** {plataforma['id']}")
                st.write(f"**Status:** {'Ativa' if plataforma['ativa'] else 'Inativa'}")
                st.write(f"**Cadastrada em:** {plataforma['data_cadastro']}")
                
                # Mostrar taxas desta plataforma
                taxas = db.get_taxas_plataforma(user_hash, plataforma['id'])
                if not taxas.empty:
                    st.write("**Taxas configuradas:**")
                    for _, taxa in taxas.iterrows():
                        if taxa['ativa']:
                            tipo_icon = "%" if taxa['tipo_taxa'] == 'percentual' else "R$"
                            st.write(f"• {taxa['nome_taxa']}: {taxa['valor']} {tipo_icon}")
                            if taxa.get('condicao') and taxa['condicao'] != 'sempre':
                                st.write(f"  Condição: {taxa['condicao']}")
                else:
                    st.warning("⚠️ Nenhuma taxa configurada para esta plataforma")
            
            with col2:
                # Ações
                if st.button(f"{'🔴 Desativar' if plataforma['ativa'] else '🟢 Ativar'}", 
                           key=f"toggle_{plataforma['id']}"):
                    success, msg = db.update_plataforma(
                        user_hash, 
                        plataforma['id'],
                        {'ativa': not plataforma['ativa']}
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                
                if st.button("🗑️ Excluir", key=f"delete_{plataforma['id']}"):
                    # Implementar confirmação antes de excluir
                    if st.checkbox(f"Confirmar exclusão de {plataforma['nome']}", 
                                 key=f"confirm_del_{plataforma['id']}"):
                        success, msg = db.delete_plataforma(user_hash, plataforma['id'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

def add_new_platform(db: DatabaseManager, user_hash: str):
    """Formulário para adicionar nova plataforma"""
    
    st.subheader("➕ Adicionar Nova Plataforma")
    
    # Sugestões de plataformas
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Plataformas populares:**")
        sugestoes = get_platform_suggestions()
        
        # Quick add buttons
        cols = st.columns(3)
        for i, sugestao in enumerate(sugestoes[:9]):
            with cols[i % 3]:
                if st.button(sugestao, key=f"quick_add_{sugestao}", use_container_width=True):
                    st.session_state[f'platform_name_input'] = sugestao
    
    with col2:
        with st.form("add_platform_form"):
            # Nome da plataforma
            nome = st.text_input(
                "Nome da Plataforma",
                value=st.session_state.get('platform_name_input', ''),
                placeholder="Ex: Shopee, Mercado Livre, etc"
            )
            
            # Status inicial
            ativa = st.checkbox("Plataforma ativa", value=True)
            
            # Botão de submit
            submitted = st.form_submit_button("Adicionar Plataforma", type="primary", use_container_width=True)
            
            if submitted:
                if not nome:
                    st.error("❌ Por favor, informe o nome da plataforma!")
                else:
                    success, msg = db.add_plataforma(user_hash, {
                        'nome': nome,
                        'ativa': ativa
                    })
                    
                    if success:
                        st.success(f"✅ {msg}")
                        # Limpar campo
                        if 'platform_name_input' in st.session_state:
                            del st.session_state['platform_name_input']
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

def configure_taxes(db: DatabaseManager, user_hash: str):
    """Interface para configurar taxas das plataformas"""
    
    st.subheader("💰 Configuração de Taxas")
    
    plataformas = db.get_plataformas(user_hash)
    
    if plataformas.empty:
        st.warning("⚠️ Cadastre pelo menos uma plataforma antes de configurar taxas!")
        return
    
    # Seleção de plataforma
    plataforma_selecionada = st.selectbox(
        "Selecione a plataforma:",
        options=plataformas['nome'].tolist(),
        format_func=lambda x: f"📦 {x}"
    )
    
    if plataforma_selecionada:
        # Obter ID da plataforma
        plataforma_id = plataformas[plataformas['nome'] == plataforma_selecionada]['id'].values[0]
        
        # Dividir em duas colunas
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📋 Taxas Configuradas")
            show_platform_taxes(db, user_hash, plataforma_id, plataforma_selecionada)
        
        with col2:
            st.markdown("### ➕ Adicionar Nova Taxa")
            add_new_tax(db, user_hash, plataforma_id, plataforma_selecionada)

def show_platform_taxes(db: DatabaseManager, user_hash: str, plataforma_id: int, plataforma_nome: str):
    """Mostra as taxas configuradas para uma plataforma"""
    
    taxas = db.get_taxas_plataforma(user_hash, plataforma_id)
    
    if taxas.empty:
        st.info(f"Nenhuma taxa configurada para {plataforma_nome}")
        
        # Sugestões rápidas
        st.write("**Sugestões de taxas comuns:**")
        sugestoes = get_tax_suggestions()[:3]
        
        for sugestao in sugestoes:
            if st.button(f"➕ {sugestao['nome']}", key=f"suggest_{sugestao['nome']}"):
                st.session_state['tax_name_input'] = sugestao['nome']
                st.session_state['tax_type_input'] = sugestao['tipo']
                st.rerun()
        return
    
    # Listar taxas existentes
    for idx, taxa in taxas.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                tipo_icon = "%" if taxa['tipo_taxa'] == 'percentual' else "R$"
                status_icon = "✅" if taxa['ativa'] else "❌"
                
                st.write(f"**{taxa['nome_taxa']}** {status_icon}")
                st.write(f"Valor: {taxa['valor']} {tipo_icon}")
                
                if taxa.get('condicao') and taxa['condicao'] != 'sempre':
                    st.write(f"📐 Condição: `{taxa['condicao']}`")
                
                if taxa.get('prioridade'):
                    st.write(f"🔢 Prioridade: {taxa['prioridade']}")
            
            with col2:
                if st.button("✏️", key=f"edit_tax_{taxa['id']}", help="Editar taxa"):
                    st.session_state[f'editing_tax_{taxa["id"]}'] = True
                    st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"del_tax_{taxa['id']}", help="Excluir taxa"):
                    success, msg = db.delete_taxa(user_hash, taxa['id'])
                    if success:
                        st.success("Taxa removida!")
                        st.rerun()
                    else:
                        st.error(msg)
            
            # Modo de edição
            if st.session_state.get(f'editing_tax_{taxa["id"]}', False):
                with st.form(f"edit_tax_form_{taxa['id']}"):
                    st.write("**Editar Taxa:**")
                    
                    novo_nome = st.text_input("Nome", value=taxa['nome_taxa'])
                    novo_valor = st.number_input(
                        "Valor",
                        value=float(taxa['valor']),
                        min_value=0.0,
                        step=0.1 if taxa['tipo_taxa'] == 'percentual' else 1.0
                    )
                    nova_condicao = st.text_input(
                        "Condição (opcional)",
                        value=taxa.get('condicao', ''),
                        placeholder="Ex: preco > 100"
                    )
                    nova_prioridade = st.number_input(
                        "Prioridade",
                        value=int(taxa.get('prioridade', 1)),
                        min_value=1,
                        max_value=99
                    )
                    nova_ativa = st.checkbox("Ativa", value=taxa['ativa'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Salvar"):
                            success, msg = db.update_taxa(user_hash, taxa['id'], {
                                'nome_taxa': novo_nome,
                                'valor': novo_valor,
                                'condicao': nova_condicao or 'sempre',
                                'prioridade': nova_prioridade,
                                'ativa': nova_ativa
                            })
                            
                            if success:
                                st.success("Taxa atualizada!")
                                del st.session_state[f'editing_tax_{taxa["id"]}']
                                st.rerun()
                            else:
                                st.error(msg)
                    
                    with col2:
                        if st.form_submit_button("❌ Cancelar"):
                            del st.session_state[f'editing_tax_{taxa["id"]}']
                            st.rerun()
            
            st.divider()

def add_new_tax(db: DatabaseManager, user_hash: str, plataforma_id: int, plataforma_nome: str):
    """Formulário para adicionar nova taxa"""
    
    with st.form("add_tax_form"):
        # Nome da taxa
        nome_taxa = st.text_input(
            "Nome da Taxa",
            value=st.session_state.get('tax_name_input', ''),
            placeholder="Ex: Comissão, Taxa por venda, etc"
        )
        
        # Tipo de taxa
        tipo_options = get_tax_type_options()
        tipo_taxa = st.selectbox(
            "Tipo de Taxa",
            options=list(tipo_options.keys()),
            format_func=lambda x: tipo_options[x],
            index=list(tipo_options.keys()).index(st.session_state.get('tax_type_input', 'percentual'))
        )
        
        # Valor
        if tipo_taxa == 'percentual':
            valor = st.number_input(
                "Valor (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                help="Percentual sobre o valor do produto"
            )
        else:
            valor = st.number_input(
                "Valor (R$)",
                min_value=0.0,
                value=0.0,
                step=0.50,
                help="Valor fixo em reais"
            )
        
        # Campos avançados em expander
        with st.expander("⚙️ Configurações Avançadas"):
            # Condição de aplicação
            st.write("**Condição de aplicação:**")
            condicao_tipo = st.radio(
                "Quando aplicar esta taxa?",
                ["Sempre", "Condição personalizada"],
                horizontal=True
            )
            
            if condicao_tipo == "Condição personalizada":
                condicao = st.text_input(
                    "Condição",
                    placeholder="Ex: preco > 100, preco <= 50",
                    help="Use 'preco' para referenciar o valor do produto"
                )
            else:
                condicao = "sempre"
            
            # Prioridade
            prioridade = st.number_input(
                "Prioridade de aplicação",
                min_value=1,
                max_value=99,
                value=50,
                help="Taxas com menor número são aplicadas primeiro"
            )
        
        # Taxa ativa
        ativa = st.checkbox("Taxa ativa", value=True)
        
        # Botão de submit
        submitted = st.form_submit_button(
            f"Adicionar Taxa para {plataforma_nome}",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not nome_taxa:
                st.error("❌ Por favor, informe o nome da taxa!")
            elif valor <= 0:
                st.error("❌ O valor da taxa deve ser maior que zero!")
            else:
                success, msg = db.add_taxa(user_hash, {
                    'plataforma_id': plataforma_id,
                    'nome_taxa': nome_taxa,
                    'tipo_taxa': tipo_taxa,
                    'valor': valor,
                    'condicao': condicao,
                    'prioridade': prioridade,
                    'ativa': ativa
                })
                
                if success:
                    st.success(f"✅ {msg}")
                    # Limpar campos do session state
                    for key in ['tax_name_input', 'tax_type_input']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")