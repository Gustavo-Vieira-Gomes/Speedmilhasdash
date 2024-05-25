import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os
import toml
import json

def cria_secrets_file():
    with open('secrets.toml', 'w+') as tom_file:
        dict_ = os.environ.get('secrets')
        dict_ = json.loads(dict_)
        secrets = toml.dump(dict_)


def pegar_planilha(worksheet: str, spreadsheet: str) -> pd.DataFrame:
    conn = st.connection('emissionsconnect', type=GSheetsConnection)
    df = conn.read(spreadsheet=spreadsheet, worksheet=worksheet)
    try:
        df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
    except: pass
    try: df.rename(columns={'Reserva': 'Localizador'}, inplace=True)
    except:pass
    df = df[df['Localizador'].isna() == False]
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def concatenar_planliha_de_custos_faturamento() -> pd.DataFrame:
    # PEGANDO TODAS AS PLANILHAS
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro' ]
    month_index = datetime.datetime.today().month - 1
    with st.spinner('Acessando planilhas'):
        faturamento = pegar_planilha(spreadsheet=os.environ.get('NOME_PLANILHA_FATURAMENTO'), worksheet='Cadastro de Emissoes')
        custo = pegar_planilha(spreadsheet=os.environ.get('NOME_PLANILHA_CUSTO'), worksheet='Fornecedores')
        voltas = pegar_planilha(spreadsheet=os.environ.get('NOME_PLANILHA_VOLTAS'), worksheet='2024')
        voltas_ = pegar_planilha(spreadsheet=os.environ.get('NOME_PLANILHA_VOLTAS'), worksheet=meses[month_index])
    # EDITANDO FATURAMENTO
    faturamento.rename(columns={'Carimbo de data/hora': 'Data da Emissao', 'Valor total da venda\n': 'Total Venda', 'Quantidade de Passageiros': 'CPFs', 'Taxas De Embarque em REAL ( Dolar e Euro converter para real )': 'Taxas De Embarque', 'Quem Emitiu': 'Emitido por'}, inplace=True)
    faturamento = faturamento[['Data da Emissao', 'Cliente', 'Localizador', 'Cia', 'Quantidade de Milhas', 'Taxas De Embarque', 'Total Venda', 'CPFs', 'Emitido por', 'Quem pagou as taxas', 'Titular', 'Login', 'Senha']]
    faturamento.drop_duplicates(subset='Localizador',keep='last', inplace=True)
    faturamento.loc[:, 'Data da Emissao'] = faturamento['Data da Emissao'].apply(lambda x: datetime.datetime.strptime(str(x), '%d/%m/%Y %H:%M:%S'))
    faturamento.set_index('Localizador', inplace=True)
    # PEGANDO CUSTO E EDITANDO DF
    custo.rename(columns={'TotalMilhas+Taxas':'Total Custo'}, inplace=True)
    custo = custo[['Localizador', 'Total Custo']]
    custo.drop_duplicates(keep='last', inplace=True, subset='Localizador')
    custo.set_index('Localizador', inplace=True)
    # PEGANDO VOLTAS E EDITANDO DF
    voltas = pd.concat([voltas, voltas_], ignore_index=True)
    voltas.rename(columns={'Data': 'Data da Emissao', 'Venda Realizada para': 'Cliente', 'Custo total':'Total Custo', 'Venda total':'Total Venda'}, inplace=True)
    voltas = voltas[['Data da Emissao', 'CPFs', 'Cliente', 'Localizador', 'Status', 'Total Custo', 'Total Venda', 'Emitido por']]
    voltas = voltas[voltas['CPFs'] != '-']
    voltas.dropna(subset='Data da Emissao', inplace=True)
    voltas.loc[:, 'Data da Emissao'] = voltas['Data da Emissao'].apply(lambda x: datetime.datetime.strptime(str(x), '%d/%m/%Y'))
    voltas['Tipo'] = ['Volta' for x in range(len(voltas.index))]
    voltas.fillna({'Status': 'A Cancelar'}, inplace=True)
    voltas['num emit'] = voltas['CPFs'].copy()
    # UNINDO OS DATAFRAMES
    df_ = pd.merge(faturamento, custo, left_index=True, right_index=True, how='inner')
    df_.reset_index(inplace=True)
    df_['Tipo'] = ['Emissao' for x in range(len(df_.index))]
    df_['num emit'] = [1 for x in range(len(df_.index))]
    df = pd.concat([df_, voltas], axis=0, ignore_index=True)
    # TRATANDO DF FINAL
    df.fillna({'Cliente': 'Não identificado', 'Cia': 'Não identificada', 'Quantidade de Milhas': 0, 'Taxas De Embarque': 0, 'Total Venda': 0, 'CPFs': 1, 'Milheiro Venda': 0, 'Milheiro Compra': 0, 'Custo Parcial': 0, 'Total Custo': 0, 'Status': '-'}, inplace=True)
    df.loc[:, 'Total Venda'] = pd.to_numeric(df['Total Venda'].apply(lambda x: str(x).replace('R$ ', '').replace(',', '.')), errors='coerce')
    df.loc[:, 'Total Custo'] = pd.to_numeric(df['Total Custo'].apply(lambda x: str(x).replace('R$ ', '').replace(',', '.')), errors='coerce')
    df['Quantidade de Milhas'] = pd.to_numeric(df['Quantidade de Milhas'], errors='coerce')
    df['Lucro'] = df['Total Venda'] - df['Total Custo']
    df.loc[:, 'Cia'] = df['Cia'].apply(lambda x: str(x).title().strip())
    df.loc[:, 'Cliente'] = df['Cliente'].apply(lambda x: str(x).title().strip())
    df.loc[:, 'CPFs'] = pd.to_numeric(df['CPFs'], errors='coerce').dropna().apply(lambda x: int(x))
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def pesquisar_logins():
    df_options = {'usernames':{}}
    conn = st.connection('emissionsconnect', type=GSheetsConnection)
    with st.spinner('Pegando os logins...'):
        df = conn.read(spreadsheet=os.environ.get('NOME_PLANILHA_LOGINS'), worksheet='logins', ttl=3600)
    try:
        df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
        df.dropna(inplace=True)
    except: pass

    for line in df.itertuples():
        df_options['usernames'][line[1]] = {'password': f'{line[3]}', 'Acesso': f'{int(line[4])}', 'name': line[2]}

    return df_options