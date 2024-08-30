import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import datetime
from sidebar import sidebar_visao_geral
import plotly.express as px


def create_pie_chart(labels, values, hole=0.4, height=200, annotation_func=lambda x: f'{int(x.sum()):0,}'.replace('.', '*').replace(',', '.').replace('*', ',')):
    """
    Cria um gráfico de pizza com os dados fornecidos.
    """

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=hole, showlegend=False, textinfo='label', textposition='inside')])
    fig.update_layout(
        margin={'t': 0, 'l': 0, 'r': 0, 'b': 20, 'pad': 0},
        height=height
    )
    if hole:
        fig.update_layout(
            annotations=[dict(text=annotation_func(values), x=0.5, y=0.5, font_size=15, showarrow=False)]
        )
    return fig


def create_bar_chart(x, y, name, marker_color):
    """
    Cria um gráfico de barras com os dados fornecidos.
    """
    fig = go.Figure(data=[go.Bar(x=x, y=y, name=name, marker_color=marker_color, opacity=0.7, orientation='v', showlegend=True, hovertemplate="R$%{y:.2f}")])
    fig.update_layout(
        margin={'t': 0, 'l': 0, 'r': 0, 'b': 20, 'pad': 0},
        height=180
    )
    return fig


def fat_total_metric(df: pd.DataFrame):
    """
    Exibe métricas de faturamento, lucro e número de emissões.
    """
    # Layout de colunas
    col1, col2, col3 = st.columns(3)

    # Faturamento
    fig_fat = create_pie_chart(df['Cliente'], df['Total Venda'], hole=None)
    with col1.expander(label='Faturamento', expanded=True):
        st.metric('Faturamento', f'R${df["Total Venda"].sum():0,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.'),
                  label_visibility='collapsed')
        if not df.empty:
            st.plotly_chart(fig_fat, use_container_width=True, config={'displayModeBar': False})

    # Lucro
    try:
        delta = ((df['Total Venda'].sum() - df['Total Custo'].sum()) / df['Total Venda'].sum()) * 100
    except ZeroDivisionError:
        delta = ''
    delta = f"{delta:.2f}%".replace('.', ',') if df['Total Venda'].sum() != 0 else None
    df_lucro = df.groupby('Cliente').sum().reset_index()
    fig_lucro = create_bar_chart(df_lucro['Cliente'], df_lucro['Lucro'], 'Lucro', 'rgba(0, 0, 255, 0.5)')
    with col2.expander(label='Lucro', expanded=True):
        st.metric('Lucro', f"R${df['Lucro'].sum():0,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'),
                  delta=delta, label_visibility='collapsed')
        if not df.empty:
            st.plotly_chart(fig_lucro, use_container_width=True, config={'displayModeBar': False})

    # Número de Emissões
    fig_emissoes = create_pie_chart(df['Cliente'], df['num emit'], hole=None)
    with col3.expander(label='Nº de Emissões', expanded=True):
        st.metric('Nº de Emissões', f"{int(df['num emit'].sum())}", label_visibility='collapsed')
        if not df.empty:
            st.plotly_chart(fig_emissoes, use_container_width=True, config={'displayModeBar': False})


def fat_total_pie_charts(df:pd.DataFrame):
    """
    Exibe o total de milhas usadas em gráfico de pizza.
    """
    st.markdown("<h3 style='text-align: center;'>Total de Milhas Usadas:</h3>", unsafe_allow_html=True)
    if not df.empty:
        df = df[df['Cia'] != 'Não identificada']
        fig = create_pie_chart(df['Cia'], df['Quantidade de Milhas'], height=280)
        st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True)
    else:
        st.write('Nenhuma milha utilizada dentro dos filtros inseridos')


def ranking_das_cias(df: pd.DataFrame):
    """
    Exibe o ranking das companhias por lucro, emissões ou faturamento.
    """
    with st.container(border=True):
        df_grouped = df.groupby('Cia', sort=True).sum()
        radio = st.radio(
            'Deseja classificar as companhias por:', 
            options=['Lucro', 'CPFs', 'Total Venda'], 
            horizontal=True, 
            format_func=lambda x: 'Faturamento' if x == 'Total Venda' else 'Emissões' if x == 'CPFs' else x
        )
        if not df.empty:
            df_sorted = df_grouped[[radio]].sort_values(by=radio, ascending=False)
            df_sorted['Classificação'] = [f'{i}º' for i in range(1, len(df_sorted) + 1)]
            df_sorted.reset_index(inplace=True)
            df_sorted.set_index('Classificação', inplace=True)
            df_sorted[radio] = df_sorted[radio].apply(lambda x: f'R${x:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.') if radio != 'CPFs' else x)
            df_sorted.rename(columns={'CPFs': 'Nº Emissões', 'Total Venda': 'Faturamento'}, inplace=True)
            st.dataframe(df_sorted, use_container_width=True, height=269)
        else:
            st.write('Nenhuma Emissão encontrada dentro dos filtros')


def fat_evolution_chart(df):
    """
    Exibe a evolução do faturamento ao longo do período especificado.
    """
    st.markdown('***Evolução do Faturamento e do Lucro***')
    num_dias_evolution = st.text_input(label='Deseja Ver a evolução a partir de quantos dias atrás?', value=7)
    if num_dias_evolution.isnumeric():
        # Filtrando o DataFrame pelo período especificado
        df.sort_values(by='Data da Emissao', ascending=True, inplace=True)
        df = df[df['Data da Emissao'] >= datetime.datetime.today() - datetime.timedelta(int(num_dias_evolution))]
        df['Data da Emissao'] = df['Data da Emissao'].apply(lambda x: x.strftime('%d/%m'))
        df = df[['Data da Emissao', 'Total Venda', 'Lucro']].groupby('Data da Emissao', sort=False).sum().reset_index()

        # Criando gráfico de barras
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Data da Emissao'], y=df['Total Venda'], name='Faturamento', marker_color='rgba(255, 0, 0, 0.5)', opacity=0.7, orientation='v', showlegend=True, hovertemplate="R$%{y:.2f}"))
        fig.add_trace(go.Bar(x=df['Data da Emissao'], y=df['Lucro'], name='Lucro', marker_color='rgba(0, 0, 255, 0.5)', opacity=0.7, orientation='v', showlegend=True, hovertemplate="R$%{y:.2f}"))
        fig.update_layout(margin={'t':0, 'l':0, 'r':0, 'b':0}, barmode='group', height=150)

        # Exibindo o gráfico
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def clientes_sem_emitir(df: pd.DataFrame):
    """
    Exibe os clientes que não emitiram há um número específico de dias.
    """
    with st.container(border=True):
        num_dias_sem_emitir = st.text_input(label='Deseja ver clientes sem emitir há quantos dias?', value=7)
        if num_dias_sem_emitir.isnumeric():
            # Renomeando coluna para 'Última Emissão'
            df.rename(columns={'Data da Emissao': 'Última Emissão'}, inplace=True)
            
            # Calculando a última emissão de cada cliente
            ultima_emissao = df.groupby('Cliente')['Última Emissão'].max().sort_values(ascending=True).reset_index()
            
            # Filtrando os clientes que não emitiram nos últimos 'num_dias_sem_emitir' dias
            agencias_filtradas = ultima_emissao[ultima_emissao['Última Emissão'] < datetime.datetime.today() - datetime.timedelta(int(num_dias_sem_emitir))]
            # Convertendo a data para o formato de string
            agencias_filtradas.loc[:, 'Última Emissão'] = agencias_filtradas['Última Emissão'].apply(lambda x: x.strftime('%d/%m/%Y'))
            
            # Exibindo os clientes
            st.dataframe(agencias_filtradas, use_container_width=True, height=253, hide_index=True)


def metricas_voltas_canceladas(df: pd.DataFrame):
    """
    Exibe métricas relacionadas a cancelamentos, voltas a cancelar e erros.
    """
    # Layout de colunas
    col1, col2, col3, col4 = st.columns(4)
    
    # Métricas
    col1.metric('Cancelamentos Feitos por nós:', value=int(df[df['Status'] == 'Cancelada']['num emit'].sum()))
    col2.metric('Cancelamentos Terceirizados:', value=int(df[(df['Status'] != 'Cancelada') & (df['Status'] != 'A Cancelar') & (df['Status'] != 'Erro')]['num emit'].sum()))
    col3.metric('Voltas a Cancelar:', value=int(df[df['Status'] == 'A Cancelar']['num emit'].sum()))
    col4.metric('Erros:', value=int(df[df['Status'] == 'Erro']['num emit'].sum()))


def debitos_clientes(df: pd.DataFrame):
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: round(x, 2))
    fig = create_pie_chart(df.iloc[:, 0], df.iloc[:, 1], height=280, annotation_func=lambda x: f'R${x.sum():0,.2f}'.replace('.', '*').replace(',', '.').replace('*', ','))
    st.markdown("<h3 style='text-align: center;'>Total de Débitos dos Clientes:</h3>", unsafe_allow_html=True)
    if not df.empty and df['Debito'].sum() != 0:
        fig = st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True)
    else:
        st.write('Nenhum débito de clientes no momento!')


def debitos_speedmilhas(df: pd.DataFrame):
    df.loc[:, 'Debito'] = df.loc[:, 'Debito'].apply(lambda x: round(x, 2))
    fig = create_pie_chart(df.iloc[:, 0], df.iloc[:, 1], height=280, annotation_func=lambda x: f'R${x.sum():0,.2f}'.replace('.', '*').replace(',', '.').replace('*', ','))
    st.markdown("<h3 style='text-align: center;'>Total de Débitos da Speedmilhas:</h3>", unsafe_allow_html=True)
    if not df.empty and df['Debito'].sum() != 0:
        fig = st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True)
    else:
        st.write('Nenhum débito da speedmilhas no momento!')


def sunburst_estoque(df: pd.DataFrame, height):
    st.markdown("<h3 style='text-align: center;'>Milhas em Estoque:</h3>", unsafe_allow_html=True)
    fig = px.sunburst(
    df,
    names='Conta',
    values='Saldo Milhas',
    path=['Conta', 'Saldo Milhas', 'Saldo Reais Formatado'],
    hover_data={
        'Conta': True,
        'Saldo Milhas': ':,',  # Formatar milhas com separador de milhar
        'Saldo Reais': ':.2f'  # Formatar reais com duas casas decimais
        }
    )
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>Saldo Milhas: %{customdata[1]:,}<br>Saldo Reais: R$ %{customdata[2]:,.2f}'
    )

    fig.update_layout(
        margin={'t': 0, 'l': 0, 'r': 0, 'b': 20, 'pad': 0},
        height=height
    )

    if not df.empty and df['Saldo Milhas'].sum() != 0 and df['Saldo Reais'].sum() != 0:
        fig = st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True)
    else:
        st.write('Nada no estoque no momento!')


def visao_geral():
    """
    Exibe a visão geral do dashboard.
    """
    # Adicionando estilos personalizados
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 1rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

    # Exibindo o sidebar
    sidebar_visao_geral(st.session_state['df'], st.session_state['date_init_range'])

    # Exibindo as métricas de faturamento
    fat_total_metric(st.session_state['filtered_df'])

    # Verificando o tipo de serviço e exibindo métricas específicas
    if st.session_state['tipo_serviço'] == 'Volta':
        metricas_voltas_canceladas(st.session_state['filtered_df'])
        fat_evolution_chart(st.session_state['df_voltas'])
    else:
        fat_evolution_chart(st.session_state['df'])

        coluna1, coluna2 = st.columns([0.6, 0.4])
        with coluna1:
            clientes_sem_emitir(st.session_state['df'])
            ranking_das_cias(st.session_state['filtered_df'])
        # Exibindo gráficos e tabelas
        with coluna2:
            with st.container(border=True):
                tab_debitos_clientes, tab_debitos_speedmilhas = st.tabs(['Débitos dos Clientes', 'Débitos da Speedmilhas'])
                with tab_debitos_clientes:
                    debitos_clientes(st.session_state['df_debitos'])
                with tab_debitos_speedmilhas:
                    debitos_speedmilhas(st.session_state['df_debitos_speedmilhas'])

            with st.container(border=True):
                tab_estoque, tab_milhas_usadas = st.tabs(['Milhas em Estoque', 'Milhas Usadas'])
                with tab_estoque:
                    sunburst_estoque(st.session_state['df_estoque'], 280)
                with tab_milhas_usadas:
                    fat_total_pie_charts(st.session_state['filtered_df'])
