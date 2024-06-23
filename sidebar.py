import streamlit as st
import datetime
import pandas as pd

def filter_data(df: pd.DataFrame, date_range, client_filter, airline_filter, service_type=None):
    """Filtra os dados com base nos parâmetros fornecidos."""
    df_filtered = df[(df['Data da Emissao'].dt.date >= date_range[0]) & (df['Data da Emissao'].dt.date < date_range[1])]
    
    if service_type and service_type != 'Geral':
        df_filtered = df_filtered[df_filtered['Tipo'] == service_type]

    if 'GERAL' not in client_filter:
        df_filtered = df_filtered[df_filtered['Cliente'].isin(client_filter)]
    
    if 'GERAL' not in airline_filter:
        df_filtered = df_filtered[df_filtered['Cia'].isin(airline_filter)]
    
    return df_filtered

def display_filters(df: pd.DataFrame, date_init_range: datetime.date, type_=1):
    """Exibe filtros na barra lateral."""
    date_range = st.date_input(':calendar: Período de Análise', [date_init_range[0], date_init_range[1]], min_value=datetime.date(2023, 6, 1), key='periodkey')
    client_options = ['GERAL'] + df['Cliente'].unique().tolist()
    airline_options = ['GERAL'] + df['Cia'].unique().tolist()

    client_filter = st.multiselect('Escolha o cliente', options=client_options, default='GERAL')
    airline_filter = st.multiselect('Escolha a Cia Aérea', options=airline_options, default='GERAL')
    service_type = st.radio('Tipo', options=['Geral', 'Volta', 'Emissao'], format_func=lambda x: 'Voltas Canceladas' if x == 'Volta' else 'Emissões' if x == 'Emissao' else 'Geral', label_visibility='collapsed') if type_ == 1 else '_'

    return date_range, client_filter, airline_filter, service_type

def sidebar_visao_geral(df: pd.DataFrame = None, date_init_range: datetime.date = None):
    with st.sidebar:
        st.header('SPEEDMILHAS')
        date_range, client_filter, airline_filter, service_type = display_filters(df, date_init_range)
    
    if len(date_range) == 2 and client_filter and airline_filter:
        st.session_state['date_init_range'] = date_range
        st.session_state['tipo_serviço'] = service_type
        st.session_state['filtered_df'] = filter_data(df, date_range, client_filter, airline_filter, service_type)
        st.session_state['df_voltas'] = df[df['Tipo'] == 'Volta']


def sidebar_cadastrar_emissao():
    with st.sidebar:
        st.header('SPEEDMILHAS')
        st.session_state['tipo de cadastro'] = st.selectbox('Qual tipo de emissão', options=['Emissão', 'Volta Cancelada'])


def sidebar_ver_emissoes(df: pd.DataFrame = None, date_init_range: datetime.date = None):
    with st.sidebar:
        st.header('SPEEDMILHAS')
        date_range, client_filter, airline_filter, _ = display_filters(df, date_init_range, 2)
        user_filter = None
        if st.session_state['nivel_acesso'] == '2':
            user_options = ['GERAL'] + df['Emitido por'].unique().tolist()
            user_filter = st.multiselect('Emitidas por', options=user_options, default='GERAL')
        localizador = st.sidebar.text_input('Procure pelo Localizador da Emissão').strip().upper()
    
    if len(date_range) == 2 and client_filter and airline_filter:        
        if localizador:
            st.session_state['searched_df'] = df[df['Localizador'] == localizador]
        else:
            df_filtered = filter_data(df, date_range, client_filter, airline_filter)
            if user_filter and 'GERAL' not in user_filter:
                df_filtered = df_filtered[df_filtered['Emitido por'].isin(user_filter)]
            st.session_state['searched_df'] = df_filtered
