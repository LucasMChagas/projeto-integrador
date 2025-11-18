"""
Módulo de Relatórios
Sistema de análise e relatórios avançados
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from backend.database import DatabaseManager
from backend.utils import format_currency, format_percentage

def show_reports_page(user_hash: str):
    """Página principal de relatórios"""
    
    st.title("📊 Relatórios e Análises")
    st.markdown("---")
    
    # Inicializar gerenciador de banco
    db = DatabaseManager()
    
    # Botão para recarregar dados (limpar cache)
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 Recarregar Dados"):
            # Limpar cache de precificações
            db._clear_cache(f"{user_hash}_precificacoes")
            st.success("✅ Dados recarregados!")
            st.rerun()
    
    # Carregar dados
    produtos = db.get_produtos(user_hash)
    plataformas = db.get_plataformas(user_hash)
    precificacoes = db.get_precificacoes(user_hash)
    taxas = db.get_taxas_plataforma(user_hash)
    
    # Debug info
    with st.expander("🔍 Informações de Debug"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Produtos", len(produtos))
        with col2:
            st.metric("Total Plataformas", len(plataformas))
        with col3:
            st.metric("Total Precificações", len(precificacoes))
        with col4:
            st.metric("Total Taxas", len(taxas))
        
        if not precificacoes.empty:
            st.write("**Colunas das precificações:**", list(precificacoes.columns))
            st.write("**Amostra dos dados:**")
            st.dataframe(precificacoes.head())
    
    if produtos.empty and plataformas.empty:
        st.warning("⚠️ Você precisa cadastrar produtos e plataformas primeiro!")
        return
    
    if precificacoes.empty:
        st.info("💡 Você ainda não tem precificações salvas. Use a Calculadora para calcular e salvar preços primeiro!")
    
    # Tabs de relatórios
    tab1, tab2, tab3 = st.tabs([
        "📈 Dashboard Executivo",
        "💰 Análise Financeira",
        "📊 Performance por Plataforma"
    ])
    
    with tab1:
        show_executive_dashboard(db, user_hash, produtos, plataformas, precificacoes, taxas)
    
    with tab2:
        show_financial_analysis(db, user_hash, produtos, plataformas, precificacoes)
    
    with tab3:
        show_platform_performance(db, user_hash, produtos, plataformas, precificacoes, taxas)

def show_executive_dashboard(db, user_hash, produtos, plataformas, precificacoes, taxas):
    """Dashboard executivo com métricas principais"""
    
    st.subheader("📈 Dashboard Executivo")
    
    # Debug - verificar se há precificações
    if st.checkbox("🔍 Debug - Ver dados brutos", key="debug_dashboard"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Precificações:**")
            st.write(f"• Total: {len(precificacoes)}")
            st.write(f"• Vazio: {precificacoes.empty}")
            if not precificacoes.empty:
                st.write(f"• Colunas: {list(precificacoes.columns)}")
        with col2:
            st.write("**Produtos:**")
            st.write(f"• Total: {len(produtos)}")
            if not produtos.empty:
                st.write(f"• IDs: {produtos['id'].tolist() if 'id' in produtos.columns else 'Sem ID'}")
        with col3:
            st.write("**Plataformas:**")
            st.write(f"• Total: {len(plataformas)}")
            if not plataformas.empty:
                st.write(f"• IDs: {plataformas['id'].tolist() if 'id' in plataformas.columns else 'Sem ID'}")
        
        if not precificacoes.empty:
            st.write("**Amostra de precificações:**")
            st.dataframe(precificacoes.head())
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_produtos = len(produtos)
        produtos_precificados = len(precificacoes['produto_id'].unique()) if not precificacoes.empty and 'produto_id' in precificacoes.columns else 0
        percentual_precificado = (produtos_precificados / total_produtos * 100) if total_produtos > 0 else 0
        
        st.metric(
            "📦 Produtos",
            total_produtos,
            f"{percentual_precificado:.0f}% precificados"
        )
    
    with col2:
        if not precificacoes.empty and 'preco_sugerido' in precificacoes.columns:
            receita_potencial = precificacoes.groupby('produto_id')['preco_sugerido'].max().sum()
        else:
            receita_potencial = 0
        
        st.metric(
            "💵 Receita Potencial",
            format_currency(receita_potencial),
            "Total de preços máximos"
        )
    
    with col3:
        if not precificacoes.empty and 'margem_real' in precificacoes.columns:
            margem_media_geral = precificacoes['margem_real'].mean()
        else:
            margem_media_geral = 0
        
        st.metric(
            "📊 Margem Média",
            format_percentage(margem_media_geral),
            "Todas as plataformas"
        )
    
    with col4:
        plataformas_ativas = len(plataformas[plataformas['ativa'] == True]) if 'ativa' in plataformas.columns else len(plataformas)
        total_taxas = len(taxas) if not taxas.empty else 0
        
        st.metric(
            "🛒 Plataformas Ativas",
            plataformas_ativas,
            f"{total_taxas} taxas configuradas"
        )
    
    st.markdown("---")
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 produtos mais lucrativos
        st.subheader("🏆 Top 5 Produtos Mais Lucrativos")
        
        if not precificacoes.empty:
            # Agrupar por produto e pegar o maior lucro
            lucro_por_produto = precificacoes.groupby('produto_id')['lucro_liquido'].max().sort_values(ascending=False).head(5)
            
            if not lucro_por_produto.empty:
                # Buscar nomes dos produtos
                nomes_produtos = []
                valores_lucro = []
                
                for prod_id, lucro in lucro_por_produto.items():
                    prod = produtos[produtos['id'] == prod_id]
                    if not prod.empty:
                        nomes_produtos.append(prod.iloc[0]['nome'])
                        valores_lucro.append(lucro)
                
                if nomes_produtos:
                    cores = ['#4CAF50', '#2196F3', '#9C27B0', '#FF9800', '#00BCD4']
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=valores_lucro,
                            y=nomes_produtos,
                            orientation='h',
                            marker_color=cores[:len(nomes_produtos)],
                            text=[format_currency(v) for v in valores_lucro],
                            textposition='outside'
                        )
                    ])
                    
                    fig.update_layout(
                        template='plotly_dark',
                        paper_bgcolor='#0E1117',
                        plot_bgcolor='#262730',
                        font=dict(color='#FAFAFA'),
                        margin=dict(l=0, r=0, t=0, b=0),
                        height=300,
                        showlegend=False,
                        xaxis=dict(showticklabels=False)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nenhuma precificação encontrada")
            else:
                st.info("Nenhuma precificação encontrada")
        else:
            st.info("Calcule preços para ver os produtos mais lucrativos")
    
    with col2:
        # Distribuição de margens por plataforma
        st.subheader("📊 Margem Média por Plataforma")
        
        if not precificacoes.empty and 'plataforma_id' in precificacoes.columns:
            margem_por_plat = []
            
            for plat_id in precificacoes['plataforma_id'].unique():
                plat = plataformas[plataformas['id'] == plat_id]
                if not plat.empty:
                    margem_media = precificacoes[precificacoes['plataforma_id'] == plat_id]['margem_real'].mean()
                    margem_por_plat.append({
                        'Plataforma': plat.iloc[0]['nome'],
                        'Margem': margem_media
                    })
            
            if margem_por_plat:
                df_margem = pd.DataFrame(margem_por_plat).sort_values('Margem', ascending=False)
                
                cores_variadas = ['#2196F3', '#4CAF50', '#9C27B0', '#FF9800', '#00BCD4', '#E91E63']
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df_margem['Plataforma'],
                        y=df_margem['Margem'],
                        marker_color=cores_variadas[:len(df_margem)],
                        text=[f"{v:.1f}%" for v in df_margem['Margem']],
                        textposition='outside'
                    )
                ])
                
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#0E1117',
                    plot_bgcolor='#262730',
                    font=dict(color='#FAFAFA'),
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=300,
                    showlegend=False,
                    yaxis=dict(showticklabels=False)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Calcule preços para ver as margens")
        else:
            st.info("Calcule preços para ver as margens por plataforma")

def show_financial_analysis(db, user_hash, produtos, plataformas, precificacoes):
    """Análise financeira detalhada"""
    
    st.subheader("💰 Análise Financeira")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtro por categoria
        categorias = ['Todas'] + produtos['categoria'].dropna().unique().tolist() if 'categoria' in produtos.columns else ['Todas']
        categoria_filtro = st.selectbox("Filtrar por Categoria", categorias)
    
    with col2:
        # Filtro por plataforma
        plataformas_lista = ['Todas'] + plataformas['nome'].tolist()
        plataforma_filtro = st.selectbox("Filtrar por Plataforma", plataformas_lista)
    
    # Aplicar filtros
    produtos_filtrados = produtos.copy()
    if categoria_filtro != 'Todas':
        produtos_filtrados = produtos_filtrados[produtos_filtrados['categoria'] == categoria_filtro]
    
    precificacoes_filtradas = precificacoes.copy()
    if plataforma_filtro != 'Todas':
        plat_id = plataformas[plataformas['nome'] == plataforma_filtro]['id'].values[0]
        precificacoes_filtradas = precificacoes_filtradas[precificacoes_filtradas['plataforma_id'] == plat_id]
    
    # Métricas financeiras
    st.markdown("---")
    st.markdown("### 📊 Métricas Financeiras")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        custo_total = produtos_filtrados['custo'].sum() if not produtos_filtrados.empty else 0
        st.metric("💸 Custo Total", format_currency(custo_total))
    
    with col2:
        if not precificacoes_filtradas.empty:
            receita_media = precificacoes_filtradas['preco_sugerido'].mean()
        else:
            receita_media = 0
        st.metric("💰 Preço Médio", format_currency(receita_media))
    
    with col3:
        if not precificacoes_filtradas.empty:
            lucro_total = precificacoes_filtradas['lucro_liquido'].sum()
        else:
            lucro_total = 0
        st.metric("💵 Lucro Total", format_currency(lucro_total))
    
    with col4:
        if not precificacoes_filtradas.empty:
            roi = (lucro_total / custo_total * 100) if custo_total > 0 else 0
        else:
            roi = 0
        st.metric("📈 ROI", format_percentage(roi))
    
    # Análise de custos
    st.markdown("---")
    st.markdown("### 💸 Análise de Custos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Composição de custos
        if not produtos_filtrados.empty:
            custo_produto = produtos_filtrados['custo'].sum()
            custo_frete = produtos_filtrados['frete'].sum() if 'frete' in produtos_filtrados.columns else 0
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=['Custo do Produto', 'Frete'],
                    values=[custo_produto, custo_frete],
                    hole=0.4,
                    marker=dict(colors=['#2196F3', '#FF9800'])
                )
            ])
            
            fig.update_layout(
                title="Composição de Custos",
                template='plotly_dark',
                paper_bgcolor='#0E1117',
                plot_bgcolor='#262730',
                font=dict(color='#FAFAFA'),
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados para análise")
    
    with col2:
        # Impacto das taxas
        if not precificacoes_filtradas.empty and 'taxa_total' in precificacoes_filtradas.columns:
            taxa_media = precificacoes_filtradas['taxa_total'].mean()
            lucro_medio = precificacoes_filtradas['lucro_liquido'].mean()
            custo_medio = produtos_filtrados['custo'].mean() if not produtos_filtrados.empty else 0
            
            fig = go.Figure(data=[
                go.Bar(
                    x=['Custo', 'Taxas', 'Lucro'],
                    y=[custo_medio, taxa_media, lucro_medio],
                    marker_color=['#9E9E9E', '#FF9800', '#4CAF50'],
                    text=[format_currency(custo_medio), format_currency(taxa_media), format_currency(lucro_medio)],
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title="Decomposição do Preço Médio",
                template='plotly_dark',
                paper_bgcolor='#0E1117',
                plot_bgcolor='#262730',
                font=dict(color='#FAFAFA'),
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Calcule preços para ver o impacto das taxas")

def show_platform_performance(db, user_hash, produtos, plataformas, precificacoes, taxas):
    """Análise de performance por plataforma"""
    
    st.subheader("📊 Performance por Plataforma")
    
    if precificacoes.empty:
        st.warning("⚠️ Você precisa calcular preços primeiro!")
        return
    
    # Criar análise por plataforma
    analise_plataformas = []
    
    for _, plat in plataformas.iterrows():
        prec_plat = precificacoes[precificacoes['plataforma_id'] == plat['id']] if 'plataforma_id' in precificacoes.columns else pd.DataFrame()
        
        if not prec_plat.empty:
            total_produtos = len(prec_plat['produto_id'].unique()) if 'produto_id' in prec_plat.columns else 0
            preco_medio = prec_plat['preco_sugerido'].mean() if 'preco_sugerido' in prec_plat.columns else 0
            margem_media = prec_plat['margem_real'].mean() if 'margem_real' in prec_plat.columns else 0
            lucro_total = prec_plat['lucro_liquido'].sum() if 'lucro_liquido' in prec_plat.columns else 0
            taxa_media = prec_plat['taxa_total'].mean() if 'taxa_total' in prec_plat.columns else 0
            
            # Contar taxas da plataforma
            num_taxas = len(taxas[taxas['plataforma_id'] == plat['id']]) if not taxas.empty else 0
            
            analise_plataformas.append({
                'Plataforma': plat['nome'],
                'Status': '✅ Ativa' if plat.get('ativa', True) else '❌ Inativa',
                'Produtos': total_produtos,
                'Preço Médio': preco_medio,
                'Margem Média (%)': margem_media,
                'Lucro Total': lucro_total,
                'Taxa Média': taxa_media,
                'Nº Taxas': num_taxas
            })
    
    if analise_plataformas:
        df_analise = pd.DataFrame(analise_plataformas)
        
        # Métricas principais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            melhor_margem = df_analise.loc[df_analise['Margem Média (%)'].idxmax()]
            st.info(f"""
            **🥇 Melhor Margem**  
            {melhor_margem['Plataforma']}: {melhor_margem['Margem Média (%)']:.1f}%
            """)
        
        with col2:
            maior_lucro = df_analise.loc[df_analise['Lucro Total'].idxmax()]
            st.info(f"""
            **💰 Maior Lucro Total**  
            {maior_lucro['Plataforma']}: {format_currency(maior_lucro['Lucro Total'])}
            """)
        
        with col3:
            menor_taxa = df_analise.loc[df_analise['Taxa Média'].idxmin()]
            st.info(f"""
            **📉 Menor Taxa Média**  
            {menor_taxa['Plataforma']}: {format_currency(menor_taxa['Taxa Média'])}
            """)
        
        st.markdown("---")
        
        # Tabela comparativa
        st.markdown("### 📋 Comparativo Detalhado")
        
        # Formatar valores para exibição
        df_display = df_analise.copy()
        df_display['Preço Médio'] = df_display['Preço Médio'].apply(format_currency)
        df_display['Margem Média (%)'] = df_display['Margem Média (%)'].apply(lambda x: f"{x:.1f}%")
        df_display['Lucro Total'] = df_display['Lucro Total'].apply(format_currency)
        df_display['Taxa Média'] = df_display['Taxa Média'].apply(format_currency)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Gráfico de radar
        st.markdown("---")
        st.markdown("### 🎯 Análise Multidimensional")
        
        # Normalizar valores para o radar (0-100)
        df_radar = df_analise.copy()
        for col in ['Produtos', 'Margem Média (%)', 'Lucro Total', 'Nº Taxas']:
            if df_radar[col].max() > 0:
                df_radar[col] = (df_radar[col] / df_radar[col].max()) * 100
        
        fig = go.Figure()
        
        cores = ['#2196F3', '#4CAF50', '#9C27B0', '#FF9800', '#00BCD4']
        
        for i, row in df_radar.iterrows():
            if i < 5:  # Limitar a 5 plataformas no radar
                fig.add_trace(go.Scatterpolar(
                    r=[row['Produtos'], row['Margem Média (%)'], row['Lucro Total'], row['Nº Taxas']],
                    theta=['Produtos', 'Margem', 'Lucro', 'Taxas'],
                    fill='toself',
                    name=row['Plataforma'],
                    line=dict(color=cores[i])
                ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='#363842',
                    tickfont=dict(color='#FAFAFA')
                ),
                angularaxis=dict(
                    gridcolor='#363842',
                    tickfont=dict(color='#FAFAFA')
                ),
                bgcolor='#262730'
            ),
            template='plotly_dark',
            paper_bgcolor='#0E1117',
            plot_bgcolor='#262730',
            font=dict(color='#FAFAFA'),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Calcule preços para ver a análise de performance")
