import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import datetime


def fat_total_metric(df: pd.DataFrame):
    with st.container():
        st.markdown("""
            <h1 style="text-align: center;"></h1>
            <p style="text-align: center;"></p>
            """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        fig_fat = go.Figure(data=[go.Pie(labels=df['Cliente'], values=df['Total Venda'], showlegend=False, textinfo='label', textposition='inside')])
        fig_fat.update_layout(
        margin={'t':0, 'l':0, 'r':0, 'b':20, 'pad': 0},
        height=200
        ) 
        with col1.expander(label='Faturamento', expanded=True):
            st.metric('Faturamento', f'R${df["Total Venda"].sum():0,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.'), label_visibility='collapsed')
            st.plotly_chart(fig_fat, use_container_width=True, config={'displayModeBar': False})
        try:
            delta = ((df['Total Venda'].sum() - df['Total Custo'].sum())/df['Total Venda'].sum()) *100
        except: delta = ''
        delta = f"{delta:.2f}%".replace('.', ',') if df['Total Venda'].sum() != 0 else None
        df_lucro = df.groupby('Cliente').sum().reset_index()
        fig_lucro = go.Figure(data=[go.Bar(x=df_lucro['Cliente'], y=df_lucro['Lucro'], showlegend=False, hoverinfo='x+y')])
        fig_lucro.update_layout(
        margin={'t':0, 'l':0, 'r':0, 'b':20, 'pad': 0},
        height=180
        )
        with col2.expander(label='Lucro', expanded=True):
            st.metric('Lucro', f"R${df['Lucro'].sum():0,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'), delta=delta, label_visibility='collapsed')
            st.plotly_chart(fig_lucro, use_container_width=True, config={'displayModeBar': False})
        
        fig_emissoes = go.Figure(data=[go.Pie(labels=df['Cliente'], values=df['num emit'], showlegend=False, textinfo='label', textposition='inside')])
        fig_emissoes.update_layout(
        margin={'t':0, 'l':0, 'r':0, 'b':20, 'pad': 0},
        height=200
        )
        with col3.expander(label='Nº de Emissões', expanded=True):
            st.metric('Nº de Emissões', f"{int(df['num emit'].sum())}", label_visibility='collapsed')
            st.plotly_chart(fig_emissoes, use_container_width=True, config={'displayModeBar': False})


def fat_total_pie_charts(df):
    with st.container():
        df[df['Cia'] != 'Não identificada']
        fig = go.Figure(data=[go.Pie(labels=df['Cia'], values=df['Quantidade de Milhas'], hole=0.4 , showlegend=False, textinfo='label', textposition='inside')])
        fig.update_layout(
        annotations=[dict(text=f'{df["Quantidade de Milhas"].sum():0,}'.replace('.', '*').replace(',', '.').replace('*', ','), x=0.5, y=0.5, font_size=10, showarrow=False)], 
        margin={'t':0, 'l':0, 'r':0, 'b':15, 'pad': 0},
        height=280
        ) 
        st.markdown("""
            <h3 style="text-align: center;">Total de Milhas Usadas:</h3>
            """, unsafe_allow_html=True
        )

        st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True)


def ranking_das_cias(df: pd.DataFrame):
    with st.container():
        df = df.groupby('Cia', sort=True).sum()
        def format_func(option):
            if option == 'Total Venda': return 'Faturamento'
            elif option == 'CPFs': return 'Emissões'
            else: return option
        radio = st.radio('Deseja classificar as companhias por:', options=['Lucro', 'CPFs', 'Total Venda'], horizontal=True, format_func=format_func)
        df = df[[radio]].sort_values(ascending=False, by=radio)
        df['Classificação'] = [f'{i}º' for i in range(1, len(df) + 1)]
        df.reset_index(inplace=True)
        df.set_index('Classificação', inplace=True)
        if radio == 'CPFs':
            df[radio]
        else:
            df[radio] = df[radio].apply(lambda x: f'R${x:,.2f}'.replace(',', '_').replace( '.', ',').replace('_', '.'))
        df.rename(columns={'CPFs': 'Nº Emissões', 'Total Venda': 'Faturamento'}, inplace=True)
        
        st.dataframe(df, use_container_width=True, height=180)


def fat_evolution_chart(df):
    with st.container():
        st.markdown('***Evolução do Faturamento no Período***')
        num_dias_evolution = st.text_input(label='Deseja Ver a evolução a partir de quantos dias atrás?', value=7)
        if num_dias_evolution.isnumeric():
            df.sort_values(by='Data da Emissao', ascending=True, inplace=True)
            df = df[df['Data da Emissao'] >= datetime.datetime.today() - datetime.timedelta(int(num_dias_evolution))]
            df.loc[:, 'Data da Emissao'] = df['Data da Emissao'].apply(lambda x: x.strftime('%d/%m'))
            df = df[['Data da Emissao','Total Venda', 'Lucro']].groupby('Data da Emissao', sort=False).sum().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['Data da Emissao'], y=df['Total Venda'], name='Faturamento', marker_color='rgba(255, 0, 0, 0.5)', opacity=0.7, orientation='v', showlegend=True, hovertemplate="R$%{y:.2f}"))
            fig.add_trace(go.Bar(x=df['Data da Emissao'], y=df['Lucro'], name='Lucro', marker_color='rgba(0, 0, 255, 0.5)', opacity=0.7, orientation='v', showlegend=True, hovertemplate="R$%{y:.2f}"))
            fig.update_layout(margin={'t':0, 'l':0, 'r':0, 'b':0}, barmode='group', height=150)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def clientes_sem_emitir(df: pd.DataFrame):
    with st.container():
        num_dias_sem_emitir = st.text_input(label='Deseja ver clientes sem emitir há quantos dias?', value=7)
        if num_dias_sem_emitir.isnumeric():
            df.rename(columns={'Data da Emissao': 'Última Emissão'}, inplace=True)
            ultima_emissao = df.groupby('Cliente')['Última Emissão'].max().sort_values(ascending=True)
            agencias_filtradas = ultima_emissao[ultima_emissao < datetime.datetime.today() - datetime.timedelta(int(num_dias_sem_emitir))]
            agencias_filtradas = agencias_filtradas.apply(lambda x: x.strftime('%d/%m/%Y'))
            st.dataframe(agencias_filtradas, use_container_width=True, height=180)
            

def metricas_voltas_canceladas(df: pd.DataFrame):
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric('Cancelamentos Feitos por nós:', value=int(df[df['Status'] == 'Cancelada']['num emit'].sum()))
        col2.metric('Cancelamentos Terceirizados:', value=int(df[(df['Status'] != 'Cancelada') & (df['Status'] != 'Não Cancelada') & (df['Status'] != 'Erro')]['num emit'].sum()))
        col3.metric('Voltas a Cancelar:', value=int(df[df['Status'] == 'Não Cancelada']['num emit'].sum()))
        col4.metric('Erros:', value=int(df[df['Status'] == 'Erro']['num emit'].sum()))
