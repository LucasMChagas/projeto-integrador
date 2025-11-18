"""
Módulo de Calculadora de Preços
Sistema principal para calcular preços com base em custos e taxas
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from backend.database import DatabaseManager
from backend.utils import (
    format_currency,
    format_percentage,
    calculate_price
)

def show_calculator_page(user_hash: str):
    """Página principal da calculadora de preços"""
    
    st.title("💰 Calculadora de Preços")
    st.markdown("---")
    
    # Inicializar gerenciador de banco
    db = DatabaseManager()
    
    # Carregar dados
    produtos = db.get_produtos(user_hash)
    plataformas = db.get_plataformas(user_hash)
    
    if produtos.empty:
        st.warning("⚠️ Você precisa cadastrar produtos primeiro!")
        st.info("Vá para a página de **📦 Produtos** para adicionar seus produtos.")
        return
    
    if plataformas.empty:
        st.warning("⚠️ Você precisa cadastrar plataformas primeiro!")
        st.info("Vá para a página de **🛒 Plataformas** para configurar suas plataformas de venda.")
        return
    
    # Tabs principais
    tab1, tab2, tab3 = st.tabs([
        "🧮 Cálculo Individual",
        "📊 Cálculo em Lote",
        "📈 Análise Comparativa"
    ])
    
    with tab1:
        calculate_individual_price(db, user_hash, produtos, plataformas)
    
    with tab2:
        calculate_batch_prices(db, user_hash, produtos, plataformas)
    
    with tab3:
        compare_platforms(db, user_hash, produtos, plataformas)

def calculate_individual_price(db: DatabaseManager, user_hash: str, produtos: pd.DataFrame, plataformas: pd.DataFrame):
    """Cálculo de preço individual para um produto"""
    
    st.subheader("🧮 Cálculo Individual de Preço")
    
    # Verificar se há dados
    if produtos.empty or plataformas.empty:
        st.warning("⚠️ Sem dados disponíveis para cálculo")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Criar lista única de produtos com SKU para evitar duplicatas
        produtos_opcoes = []
        for idx, row in produtos.iterrows():
            opcao = f"{row['nome']} - SKU: {row['sku']}"
            produtos_opcoes.append(opcao)
        
        # Seleção de produto
        produto_selecionado = st.selectbox(
            "Selecione o Produto",
            options=produtos_opcoes
        )
        
        if produto_selecionado:
            # Extrair o SKU da seleção
            sku_selecionado = produto_selecionado.split("SKU: ")[1]
            produto_info = produtos[produtos['sku'] == sku_selecionado].iloc[0]
            
            # Mostrar informações do produto
            st.info(f"""
            **Nome:** {produto_info['nome']}  
            **SKU:** {produto_info['sku']}  
            **Custo:** {format_currency(produto_info['custo'])}  
            **Frete:** {format_currency(produto_info.get('frete', 0))}  
            **Categoria:** {produto_info.get('categoria', 'N/A')}
            """)
            
            # Permitir ajuste de valores
            st.markdown("### ✏️ Ajustar Valores (opcional)")
            
            custo_ajustado = st.number_input(
                "Custo do Produto (R$)",
                value=float(produto_info['custo']),
                min_value=0.0,
                step=0.01,
                help="Você pode ajustar o custo para simular diferentes cenários"
            )
            
            frete_ajustado = st.number_input(
                "Frete (R$)",
                value=float(produto_info.get('frete', 0)),
                min_value=0.0,
                step=0.01,
                help="Custo de envio/frete do produto"
            )
    
    with col2:
        # Seleção de plataforma
        plataforma_selecionada = st.selectbox(
            "Selecione a Plataforma",
            options=plataformas['nome'].tolist()
        )
        
        if plataforma_selecionada:
            plataforma_info = plataformas[plataformas['nome'] == plataforma_selecionada].iloc[0]
            
            # Buscar taxas da plataforma
            taxas = db.get_taxas_plataforma(user_hash)
            
            # Verificar se há taxas e se têm a estrutura correta
            if not taxas.empty and 'plataforma_id' in taxas.columns:
                taxas_plataforma = taxas[taxas['plataforma_id'] == plataforma_info['id']]
            else:
                taxas_plataforma = pd.DataFrame()
            
            if not taxas_plataforma.empty:
                st.info(f"**{len(taxas_plataforma)} taxa(s) configurada(s) para {plataforma_selecionada}**")
                
                # Mostrar resumo das taxas
                with st.expander("📋 Ver Detalhes das Taxas"):
                    for idx, taxa in taxas_plataforma.iterrows():
                        # Acessar valores de forma segura
                        tipo_taxa = taxa.get('tipo_taxa', 'percentual') if hasattr(taxa, 'get') else taxa['tipo_taxa'] if 'tipo_taxa' in taxa.index else 'percentual'
                        valor = taxa.get('valor', 0) if hasattr(taxa, 'get') else taxa['valor'] if 'valor' in taxa.index else 0
                        nome = taxa.get('nome', 'Taxa sem nome') if hasattr(taxa, 'get') else taxa['nome'] if 'nome' in taxa.index else 'Taxa sem nome'
                        ativa = taxa.get('ativa', True) if hasattr(taxa, 'get') else taxa['ativa'] if 'ativa' in taxa.index else True
                        condicao = taxa.get('condicao', '') if hasattr(taxa, 'get') else taxa['condicao'] if 'condicao' in taxa.index else ''
                        
                        if tipo_taxa == 'percentual':
                            valor_str = format_percentage(valor)
                        else:
                            valor_str = format_currency(valor)
                        
                        status = "✅ Ativa" if ativa else "❌ Inativa"
                        st.write(f"• **{nome}**: {valor_str} - {status}")
                        
                        if pd.notna(condicao) and condicao != 'sempre' and condicao != '':
                            st.caption(f"  Condição: {condicao}")
            else:
                st.warning(f"⚠️ Nenhuma taxa configurada para {plataforma_selecionada}")
            
            # Margem de lucro desejada
            st.markdown("### 💵 Margem de Lucro")
            
            margem_desejada = st.slider(
                "Margem de Lucro Desejada (%)",
                min_value=0,
                max_value=100,
                value=30,
                step=1,
                help="Percentual de lucro desejado sobre o preço final"
            )
    
    st.markdown("---")
    
    # Botão de calcular
    if st.button("🧮 Calcular Preço", type="primary", use_container_width=True):
        if produto_selecionado and plataforma_selecionada:
            
            # Preparar taxas para cálculo - converter DataFrame para lista de dicts de forma segura
            if not taxas_plataforma.empty:
                taxas_dict = []
                for idx, row in taxas_plataforma.iterrows():
                    taxa_item = {}
                    # Acessar cada coluna de forma segura
                    for col in taxas_plataforma.columns:
                        try:
                            taxa_item[col] = row[col]
                        except:
                            taxa_item[col] = None
                    taxas_dict.append(taxa_item)
            else:
                taxas_dict = []
            
            # Calcular preço
            resultado = calculate_price(
                custo=custo_ajustado,
                frete=frete_ajustado,
                taxas=taxas_dict,
                margem_desejada=margem_desejada / 100
            )
            
            # SALVAR RESULTADO NO SESSION STATE
            st.session_state['ultimo_resultado'] = resultado
            st.session_state['ultimo_produto_info'] = produto_info
            st.session_state['ultimo_plataforma_info'] = plataforma_info
            st.session_state['ultimo_custo'] = custo_ajustado
            st.session_state['ultimo_frete'] = frete_ajustado
            st.session_state['ultima_margem'] = margem_desejada
            
            if 'erro' in resultado:
                st.error(f"❌ {resultado['erro']}")
            else:
                # Mostrar resultados
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "💰 Preço Sugerido",
                        format_currency(resultado['preco_sugerido']),
                        help="Preço final sugerido para venda"
                    )
                
                with col2:
                    st.metric(
                        "💵 Lucro Líquido",
                        format_currency(resultado['lucro_liquido']),
                        f"{resultado['margem_real']}%",
                        help="Lucro após descontar custos e taxas"
                    )
                
                with col3:
                    st.metric(
                        "📊 Total de Taxas",
                        format_currency(resultado['taxa_total']),
                        f"Fixas: {format_currency(resultado['taxa_fixa'])}",
                        help="Total de taxas aplicadas"
                    )
                
                # Detalhamento
                with st.expander("📊 Ver Detalhamento Completo"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 📥 Custos")
                        st.write(f"• Custo do produto: {format_currency(custo_ajustado)}")
                        st.write(f"• Frete: {format_currency(frete_ajustado)}")
                        st.write(f"• **Custo total:** {format_currency(resultado['custo_total'])}")
                    
                    with col2:
                        st.markdown("### 📤 Receitas")
                        st.write(f"• Preço de venda: {format_currency(resultado['preco_sugerido'])}")
                        st.write(f"• Taxas totais: -{format_currency(resultado['taxa_total'])}")
                        st.write(f"• **Lucro líquido:** {format_currency(resultado['lucro_liquido'])}")
                    
                    st.markdown("### 📈 Análise de Margem")
                    st.write(f"• Margem desejada: {margem_desejada}%")
                    st.write(f"• Margem real obtida: {resultado['margem_real']}%")
                    
                    if abs(resultado['margem_real'] - margem_desejada) > 1:
                        st.warning("⚠️ A margem real difere da desejada devido às taxas aplicadas")
                
                # Salvar precificação
                st.markdown("---")
                
                salvar_col1, salvar_col2 = st.columns([3, 1])
                
                with salvar_col1:
                    observacoes = st.text_area(
                        "Observações (opcional)",
                        placeholder="Adicione observações sobre esta precificação..."
                    )
                
               
    # NOVA SEÇÃO: Botão de salvar INDEPENDENTE do cálculo
    st.markdown("---")
    st.markdown("### 💾 Salvar Última Precificação")
    
    # Verificar se há resultado calculado no session state
    if 'ultimo_resultado' in st.session_state:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            resultado_session = st.session_state.get('ultimo_resultado', {})
            produto_session = st.session_state.get('ultimo_produto_info', {})
            plataforma_session = st.session_state.get('ultimo_plataforma_info', {})
            
            # Corrigir verificação - não usar Series como booleano
            tem_dados = (
                isinstance(resultado_session, dict) and resultado_session and
                isinstance(produto_session, (dict, pd.Series)) and
                isinstance(plataforma_session, (dict, pd.Series))
            )
            
            if tem_dados:
                # Converter Series para dict se necessário
                if isinstance(produto_session, pd.Series):
                    produto_dict = produto_session.to_dict()
                else:
                    produto_dict = produto_session
                    
                if isinstance(plataforma_session, pd.Series):
                    plataforma_dict = plataforma_session.to_dict()
                else:
                    plataforma_dict = plataforma_session
                
                st.success(f"""
                ✅ Última precificação calculada:  
                **Produto:** {produto_dict.get('nome', 'N/A')}  
                **Plataforma:** {plataforma_dict.get('nome', 'N/A')}  
                **Preço:** {format_currency(resultado_session.get('preco_sugerido', 0))}
                """)
        
        with col2:
            if tem_dados and st.button("💾 Salvar Esta Precificação", key="btn_save_independent"):
                print("\n" + "!" * 60)
                print("BOTÃO INDEPENDENTE FOI CLICADO!")
                print("!" * 60)
                
                # Recuperar dados do session state
                try:
                    # Converter para dict se for Series
                    if isinstance(produto_session, pd.Series):
                        produto_dict = produto_session.to_dict()
                    else:
                        produto_dict = produto_session
                        
                    if isinstance(plataforma_session, pd.Series):
                        plataforma_dict = plataforma_session.to_dict()
                    else:
                        plataforma_dict = plataforma_session
                    
                    precificacao_data = {
                        'produto_id': produto_dict['id'],
                        'plataforma_id': plataforma_dict['id'],
                        'custo': st.session_state.get('ultimo_custo', 0),
                        'frete': st.session_state.get('ultimo_frete', 0),
                        'preco_sugerido': resultado_session['preco_sugerido'],
                        'margem_desejada': st.session_state.get('ultima_margem', 0),
                        'margem_real': resultado_session['margem_real'],
                        'lucro_liquido': resultado_session['lucro_liquido'],
                        'taxa_total': resultado_session['taxa_total'],
                        'observacoes': ''
                    }
                    
                    print(f"Dados: {precificacao_data}")
                    
                    success, msg = db.save_precificacao(user_hash, precificacao_data)
                    
                    if success:
                        st.balloons()
                        st.success(f"✅ {msg}")
                        # Limpar session state
                        for key in ['ultimo_resultado', 'ultimo_produto_info', 'ultimo_plataforma_info', 
                                   'ultimo_custo', 'ultimo_frete', 'ultima_margem']:
                            if key in st.session_state:
                                del st.session_state[key]
                    else:
                        st.error(f"❌ {msg}")
                        
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {e}")
                    print(f"ERRO: {e}")
                    import traceback
                    print(traceback.format_exc())
    else:
        st.info("💡 Calcule um preço primeiro para poder salvar")

def calculate_batch_prices(db: DatabaseManager, user_hash: str, produtos: pd.DataFrame, plataformas: pd.DataFrame):
    """Cálculo de preços em lote"""
    
    st.subheader("📊 Cálculo em Lote")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Criar lista única de produtos com SKU
        produtos_opcoes = []
        for idx, row in produtos.iterrows():
            opcao = f"{row['nome']} - SKU: {row['sku']}"
            produtos_opcoes.append(opcao)
        
        # Seleção múltipla de produtos
        produtos_selecionados = st.multiselect(
            "Selecione os Produtos",
            options=produtos_opcoes,
            default=[]
        )
    
    with col2:
        # Seleção de plataforma
        plataforma_selecionada = st.selectbox(
            "Selecione a Plataforma",
            options=plataformas['nome'].tolist(),
            key="batch_platform"
        )
    
    with col3:
        # Margem padrão
        margem_padrao = st.number_input(
            "Margem de Lucro Padrão (%)",
            min_value=0,
            max_value=100,
            value=30,
            step=1
        )
    
    if produtos_selecionados and plataforma_selecionada:
        st.markdown("---")
        
        if st.button("🧮 Calcular Preços em Lote", type="primary", use_container_width=True):
            # Obter informações da plataforma
            plataforma_info = plataformas[plataformas['nome'] == plataforma_selecionada].iloc[0]
            
            # Buscar taxas
            taxas = db.get_taxas_plataforma(user_hash)
            taxas_plataforma = taxas[taxas['plataforma_id'] == plataforma_info['id']] if not taxas.empty and 'plataforma_id' in taxas.columns else pd.DataFrame()
            
            # Converter taxas de forma segura
            taxas_dict = []
            if not taxas_plataforma.empty:
                for idx, row in taxas_plataforma.iterrows():
                    taxa_item = {}
                    for col in taxas_plataforma.columns:
                        try:
                            taxa_item[col] = row[col]
                        except:
                            taxa_item[col] = None
                    taxas_dict.append(taxa_item)
            
            # Calcular para cada produto
            resultados = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, produto_selecionado in enumerate(produtos_selecionados):
                # Extrair SKU da seleção
                sku_selecionado = produto_selecionado.split("SKU: ")[1]
                produto_info = produtos[produtos['sku'] == sku_selecionado].iloc[0]
                
                status_text.text(f"Calculando {produto_info['nome']}...")
                
                resultado = calculate_price(
                    custo=float(produto_info['custo']),
                    frete=float(produto_info.get('frete', 0)),
                    taxas=taxas_dict,
                    margem_desejada=margem_padrao / 100
                )
                
                if 'erro' not in resultado:
                    resultados.append({
                        'Produto': produto_info['nome'],
                        'SKU': produto_info['sku'],
                        'Custo': produto_info['custo'],
                        'Frete': produto_info.get('frete', 0),
                        'Preço Sugerido': resultado['preco_sugerido'],
                        'Lucro Líquido': resultado['lucro_liquido'],
                        'Margem Real (%)': resultado['margem_real'],
                        'Total Taxas': resultado['taxa_total']
                    })
                
                progress_bar.progress((idx + 1) / len(produtos_selecionados))
            
            status_text.empty()
            progress_bar.empty()
            
            if resultados:
                # Criar DataFrame com resultados
                df_resultados = pd.DataFrame(resultados)
                
                # Mostrar estatísticas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total de Produtos", len(df_resultados))
                
                with col2:
                    lucro_total = df_resultados['Lucro Líquido'].sum()
                    st.metric("Lucro Total", format_currency(lucro_total))
                
                with col3:
                    margem_media = df_resultados['Margem Real (%)'].mean()
                    st.metric("Margem Média", f"{margem_media:.1f}%")
                
                with col4:
                    preco_medio = df_resultados['Preço Sugerido'].mean()
                    st.metric("Preço Médio", format_currency(preco_medio))
                
                st.markdown("---")
                
                # Mostrar tabela de resultados
                st.markdown("### 📋 Resultados Detalhados")
                
                # Formatar valores para exibição
                df_display = df_resultados.copy()
                df_display['Custo'] = df_display['Custo'].apply(format_currency)
                df_display['Frete'] = df_display['Frete'].apply(format_currency)
                df_display['Preço Sugerido'] = df_display['Preço Sugerido'].apply(format_currency)
                df_display['Lucro Líquido'] = df_display['Lucro Líquido'].apply(format_currency)
                df_display['Total Taxas'] = df_display['Total Taxas'].apply(format_currency)
                df_display['Margem Real (%)'] = df_display['Margem Real (%)'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(df_display, use_container_width=True)
                
                # Opções de exportação
                st.markdown("### 💾 Exportar Resultados")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download Excel
                    excel_data = export_batch_results(df_resultados)
                    st.download_button(
                        label="📥 Baixar Excel",
                        data=excel_data,
                        file_name=f"precificacao_lote_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                with col2:
                    # Salvar todos no banco
                    if st.button("💾 Salvar Todas as Precificações", use_container_width=True):
                        saved_count = 0
                        for _, row in df_resultados.iterrows():
                            produto_info = produtos[produtos['sku'] == row['SKU']].iloc[0]
                            
                            precificacao_data = {
                                'produto_id': produto_info['id'],
                                'plataforma_id': plataforma_info['id'],
                                'custo': row['Custo'],
                                'frete': row['Frete'],
                                'preco_sugerido': row['Preço Sugerido'],
                                'margem_desejada': margem_padrao,
                                'margem_real': row['Margem Real (%)'],
                                'lucro_liquido': row['Lucro Líquido'],
                                'taxa_total': row['Total Taxas']
                            }
                            
                            success, _ = db.save_precificacao(user_hash, precificacao_data)
                            if success:
                                saved_count += 1
                        
                        st.success(f"✅ {saved_count} precificações salvas com sucesso!")
    else:
        st.info("👆 Selecione produtos e plataforma para calcular preços em lote")

def compare_platforms(db: DatabaseManager, user_hash: str, produtos: pd.DataFrame, plataformas: pd.DataFrame):
    """Comparação de preços entre plataformas"""
    
    st.subheader("📈 Análise Comparativa entre Plataformas")
    
    # Criar lista única de produtos com SKU
    produtos_opcoes = []
    for idx, row in produtos.iterrows():
        opcao = f"{row['nome']} - SKU: {row['sku']}"
        produtos_opcoes.append(opcao)
    
    # Seleção de produto
    produto_selecionado = st.selectbox(
        "Selecione o Produto para Comparar",
        options=produtos_opcoes,
        key="compare_product"
    )
    
    # Margem desejada
    margem_comparacao = st.slider(
        "Margem de Lucro para Comparação (%)",
        min_value=0,
        max_value=100,
        value=30,
        step=1,
        key="compare_margin"
    )
    
    if produto_selecionado:
        # Extrair SKU da seleção
        sku_selecionado = produto_selecionado.split("SKU: ")[1]
        produto_info = produtos[produtos['sku'] == sku_selecionado].iloc[0]
        
        # Mostrar info do produto
        st.info(f"""
        **Produto:** {produto_info['nome']}  
        **SKU:** {produto_info['sku']}  
        **Custo Base:** {format_currency(produto_info['custo'])}  
        **Frete:** {format_currency(produto_info.get('frete', 0))}
        """)
        
        st.markdown("---")
        
        if st.button("📊 Comparar Plataformas", type="primary", use_container_width=True):
            # Calcular para cada plataforma
            comparacoes = []
            taxas_db = db.get_taxas_plataforma(user_hash)
            
            for _, plataforma in plataformas.iterrows():
                # Buscar taxas da plataforma
                if not taxas_db.empty and 'plataforma_id' in taxas_db.columns:
                    taxas_plataforma = taxas_db[taxas_db['plataforma_id'] == plataforma['id']]
                else:
                    taxas_plataforma = pd.DataFrame()
                
                # Converter taxas de forma segura
                taxas_dict = []
                if not taxas_plataforma.empty:
                    for idx, row in taxas_plataforma.iterrows():
                        taxa_item = {}
                        for col in taxas_plataforma.columns:
                            try:
                                taxa_item[col] = row[col]
                            except:
                                taxa_item[col] = None
                        taxas_dict.append(taxa_item)
                
                # Calcular preço usando o produto correto
                resultado = calculate_price(
                    custo=float(produto_info['custo']),
                    frete=float(produto_info.get('frete', 0)),
                    taxas=taxas_dict,
                    margem_desejada=margem_comparacao / 100
                )
                
                if 'erro' not in resultado:
                    comparacoes.append({
                        'Plataforma': plataforma['nome'],
                        'Preço Sugerido': resultado['preco_sugerido'],
                        'Lucro Líquido': resultado['lucro_liquido'],
                        'Margem Real': resultado['margem_real'],
                        'Total Taxas': resultado['taxa_total'],
                        'Taxa Fixa': resultado['taxa_fixa'],
                        'Taxa %': resultado['taxa_percentual']
                    })
            
            if comparacoes:
                # Criar DataFrame
                df_comparacao = pd.DataFrame(comparacoes)
                df_comparacao = df_comparacao.sort_values('Lucro Líquido', ascending=False)
                
                # Mostrar melhor opção
                melhor_opcao = df_comparacao.iloc[0]
                
                st.success(f"""
                🏆 **Melhor Plataforma:** {melhor_opcao['Plataforma']}  
                💰 **Maior Lucro:** {format_currency(melhor_opcao['Lucro Líquido'])}  
                📊 **Margem Real:** {melhor_opcao['Margem Real']:.1f}%
                """)
                
                # Gráficos comparativos
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de barras - Lucro por plataforma
                    import plotly.graph_objects as go
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=df_comparacao['Plataforma'],
                            y=df_comparacao['Lucro Líquido'],
                            marker_color=['#4CAF50' if p == melhor_opcao['Plataforma'] else '#9E9E9E' 
                                         for p in df_comparacao['Plataforma']],
                            text=[format_currency(v) for v in df_comparacao['Lucro Líquido']],
                            textposition='outside',
                            textfont=dict(color='#FAFAFA')
                        )
                    ])
                    
                    fig.update_layout(
                        title=dict(
                            text="Lucro Líquido por Plataforma",
                            font=dict(color='#FAFAFA')
                        ),
                        template='plotly_dark',
                        paper_bgcolor='#0E1117',
                        plot_bgcolor='#262730',
                        font=dict(color='#FAFAFA'),
                        xaxis=dict(
                            tickfont=dict(color='#FAFAFA')
                        ),
                        yaxis=dict(
                            tickfont=dict(color='#FAFAFA')
                        ),
                        showlegend=False,
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Gráfico de pizza - Distribuição de taxas com cores variadas
                    cores_variadas = ['#2196F3', '#4CAF50', '#9C27B0', '#FF9800', '#00BCD4', '#E91E63', '#FFC107', '#795548']
                    
                    fig2 = go.Figure(data=[
                        go.Pie(
                            labels=df_comparacao['Plataforma'],
                            values=df_comparacao['Total Taxas'],
                            hole=0.4,
                            marker=dict(colors=cores_variadas[:len(df_comparacao)]),
                            textfont=dict(color='#FAFAFA')
                        )
                    ])
                    
                    fig2.update_layout(
                        title=dict(
                            text="Total de Taxas por Plataforma",
                            font=dict(color='#FAFAFA')
                        ),
                        template='plotly_dark',
                        paper_bgcolor='#0E1117',
                        plot_bgcolor='#262730',
                        font=dict(color='#FAFAFA'),
                        legend=dict(
                            font=dict(color='#FAFAFA')
                        ),
                        height=400
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Tabela comparativa detalhada
                st.markdown("### 📊 Tabela Comparativa Completa")
                
                df_display = df_comparacao.copy()
                df_display['Preço Sugerido'] = df_display['Preço Sugerido'].apply(format_currency)
                df_display['Lucro Líquido'] = df_display['Lucro Líquido'].apply(format_currency)
                df_display['Total Taxas'] = df_display['Total Taxas'].apply(format_currency)
                df_display['Taxa Fixa'] = df_display['Taxa Fixa'].apply(format_currency)
                df_display['Margem Real'] = df_display['Margem Real'].apply(lambda x: f"{x:.1f}%")
                df_display['Taxa %'] = df_display['Taxa %'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(df_display, use_container_width=True)
                
                # Insights
                st.markdown("### 💡 Insights da Análise")
                
                # Diferença entre melhor e pior
                pior_opcao = df_comparacao.iloc[-1]
                diferenca_lucro = melhor_opcao['Lucro Líquido'] - pior_opcao['Lucro Líquido']
                diferenca_percentual = (diferenca_lucro / pior_opcao['Lucro Líquido'] * 100) if pior_opcao['Lucro Líquido'] > 0 else 0
                
                st.info(f"""
                📊 **Análise Comparativa para {produto_info['nome']} (SKU: {produto_info['sku']})**:
                • A plataforma **{melhor_opcao['Plataforma']}** oferece {format_currency(diferenca_lucro)} a mais de lucro que **{pior_opcao['Plataforma']}**
                • Isso representa uma diferença de {diferenca_percentual:.1f}% no lucro líquido
                • A taxa média entre plataformas é de {df_comparacao['Taxa %'].mean():.1f}%
                • Custo base do produto: {format_currency(produto_info['custo'])}
                • Frete: {format_currency(produto_info.get('frete', 0))}
                """)
            else:
                st.warning("⚠️ Não foi possível calcular preços para nenhuma plataforma. Verifique se há taxas configuradas.")
def export_batch_results(df: pd.DataFrame) -> bytes:
    """Exporta resultados do cálculo em lote para Excel"""
    import io
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Precificação')
        
        # Adicionar aba de resumo
        resumo = pd.DataFrame({
            'Métrica': ['Total de Produtos', 'Lucro Total', 'Margem Média', 'Preço Médio'],
            'Valor': [
                len(df),
                f"R$ {df['Lucro Líquido'].sum():,.2f}",
                f"{df['Margem Real (%)'].mean():.1f}%",
                f"R$ {df['Preço Sugerido'].mean():,.2f}"
            ]
        })
        resumo.to_excel(writer, index=False, sheet_name='Resumo')
    
    return output.getvalue()