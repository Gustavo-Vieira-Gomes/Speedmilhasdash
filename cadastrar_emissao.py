import streamlit as st
import pandas as pd
import gspread as gc
from sidebar import sidebar_cadastrar_emissao
import datetime
import os


def cadastrar_dados(values: list, planilha):
    """
    Cadastra os dados na planilha especificada.
    """
    # Selecionar planilha
    if planilha == 'Volta Cancelada':
        conn = gc.service_account(filename='speedmilhas_credentials.json')
        spreadsheet = conn.open_by_key(os.environ.get('ID_PLANILHA_VOLTAS_CANCELADAS'))
        sheet = spreadsheet.worksheet('Maio')
    elif planilha == 'Emissão':
        conn = gc.service_account(filename='speedmilhas_credentials.json')
        spreadsheet = conn.open_by_key(os.environ['ID_PLANILHA_EMISSOES'])
        sheet = spreadsheet.worksheet('Cadastro de Emissoes')

    # Obter último índice
    valores = sheet.col_values(5)
    ultimo_index = [i for i in zip(valores, range(1, len(valores) + 1)) if i[0] != ''][-1][-1] + 1
    if planilha == 'Volta Cancelada':
        values.insert(0, ultimo_index - 1)
    
    # Inserir dados na planilha
    try:
        sheet.insert_row(values=values, index=ultimo_index, inherit_from_before=False)
    except Exception as e:
        st.error('Não foi possível realizar o cadastro')
    else:
        st.success('Cadastro realizado com sucesso')


def verificar_input_de_dados(**kwargs):
    for kwarg in kwargs['obrigatorios']:
        print(kwargs['obrigatorios'])
        if kwarg == '' or kwarg is None:
            st.error('Dados incompletos. Tente novamente!')
            return
    try: 
        cadastrar_dados(kwargs['values'], kwargs['planilha'])
    except Exception as e: 
        st.error('Não foi possível realizar o cadastro')


def formulario_de_cadastro():
    """
    Exibe o formulário de cadastro de emissões ou voltas canceladas.
    """
    sidebar_cadastrar_emissao()
    if st.session_state['tipo de cadastro'] == 'Emissão':
        with st.form(clear_on_submit=True, key='Cadastro de emissoes'):
            st.subheader('Cadastro de Emissões:')
            col1, col2, col3 = st.columns(3)
            cliente = col1.text_input(label='Nome do Cliente', key='cliente')
            quantidade_milhas = col2.number_input(label='Número de Milhas', min_value=0, key='quantidade_milhas')
            localizador = col3.text_input(label='Localizador', key='localizador')
            valor_total = col1.number_input(label='Valor da venda', min_value=0.0, key='valor_total')
            cia_aerea = col2.text_input(label='Companhia Aérea', key='cia_aerea')
            emissor = col3.text_input('Quem emitiu?', key='emissor')
            data_ida = col1.date_input(label='Data da Ida', value=datetime.date.today(), key='data_ida')
            forma_de_pagamento = col2.selectbox('Forma de Pagamento', options=['Pix', 'Cartão', 'Faturado'], key='forma_de_pagamento')
            titular = col3.text_input('Nome do Titular', key='titular')
            valor_pago_no_cartao = col2.number_input(label='Valor pago no cartão', min_value=0.0, key='valor_pago_no_cartao')
            quem_pagou_as_taxas = col3.text_input(label='Quem pagou as taxas', key='quem_pagou_as_taxas')
            login = col1.text_input('Login da conta', key='login')
            taxa_embarque = col2.number_input(label='Valor da Taxa de Embarque', key='taxa_embarque', min_value=0.0)
            quantidade_passageiros = col2.number_input(label='Quantidade de passageiros', min_value=0, key='quantidade_passageiros')
            senha = col1.text_input('Senha da conta', key='senha')
            data_volta = col1.date_input(label='Data da Volta', value=datetime.date.today(), key='data_volta')
            possui_volta = col1.checkbox('Deseja incluir data da volta?', key='possui_volta')
            observacoes = col3.text_area('Observações sobre a Emissão', key='observacoes', height=125)
            fomos_pagos = col2.checkbox('Já fomos pagos?', value=False, key='fomos_pagos')
            data_volta = data_volta.strftime('%d/%m/%Y') if possui_volta else '-'
            data_cadastro = datetime.datetime.now()
            try:
                milheiro = (valor_total - taxa_embarque) / quantidade_milhas
            except:
                milheiro = 0
            user = st.session_state['username']
            submit_button = st.form_submit_button('Cadastrar', type='primary')
            if submit_button:
                verificar_input_de_dados(
                    obrigatorios=[data_cadastro.strftime('%d/%m/%Y %H:%M'), cliente, data_ida.strftime('%d/%m/%Y'), data_volta, localizador, cia_aerea, quantidade_milhas, taxa_embarque,
                            quem_pagou_as_taxas, titular, login, senha, emissor, forma_de_pagamento, user, valor_total, valor_pago_no_cartao, quantidade_passageiros, milheiro, fomos_pagos],
                    values=[data_cadastro.strftime('%d/%m/%Y %H:%M'), cliente, data_ida.strftime('%d/%m/%Y'), data_volta, localizador, cia_aerea, quantidade_milhas, taxa_embarque,
                            quem_pagou_as_taxas, titular, login, senha, emissor, forma_de_pagamento, user, valor_total, valor_pago_no_cartao, quantidade_passageiros, milheiro, fomos_pagos, observacoes],
                    planilha=st.session_state['tipo de cadastro']
                )
    else:
        with st.form(key='cadastro voltas', clear_on_submit=True):
            st.subheader('Cadastro de Voltas Canceladas:')          
            col1, col2, col3 = st.columns(3)
            quantidade_passageiros = col1.number_input('Número de CPFs', min_value=1, key='quantidade_passageiros')
            cliente = col2.text_input('Cliente', key='cliente')
            valor_da_venda_por_cpf = col3.number_input('Valor da venda por CPF', min_value=0.0, key='valor_da_venda_por_cpf')
            localizador = col1.text_input('Localizador', key='localizador')
            custo_por_cpf = col2.number_input('Custo da venda por CPF', min_value=0.0, value=0.0, key='custo_por_cpf')
            status = col3.selectbox(label='Situação de Cancelamento', options=['Cancelada', 'A Cancelar', 'Daniel', 'Márcio'], key='status')
            conta = col1.text_input('Conta utilizada', key='conta')
            valor_pago_no_cartao = col2.number_input('Valor pago no Cartão', min_value=0.0, key='valor_pago_no_cartao')
            data_chegada = col3.date_input('Data de chegada', value=datetime.datetime.today(), key='data_chegada')
            emissor = col1.text_input('Quem emitiu?', key='emissor')
            sobrenome_passageiro = col2.text_input('Sobrenome do passageiro', key='sobrenome_passageiro')
            horario_chegada = col3.time_input('Horário da chegada', value=datetime.time(12, 00), key='horario_chegada')
            cartao = col1.text_input('Cartão Usado', key='cartao')
            observacoes = col2.text_area('Observações',  key='observacoes')
            pagamento_conferido = col3.checkbox('Pagamento conferido no extrato?', value=False, key= 'pagamento_conferido')
            data_cadastro = datetime.datetime.now()
            submit_button = st.form_submit_button('Cadastrar', type='primary')
            if submit_button:
                try:
                    data_hora_chegada = datetime.datetime.combine(data_chegada, horario_chegada).strftime('Cancelar %d/%m %Hh%M')
                except:
                    data_hora_chegada = '-'
                custo_total = custo_por_cpf * quantidade_passageiros
                venda_total = valor_da_venda_por_cpf * quantidade_passageiros
                pagamento_conferido = 'Sim' if pagamento_conferido else 'Não'
                verificar_input_de_dados(
                    obrigatorios=[data_cadastro.strftime('%d/%m/%Y %H:%M'), conta, custo_por_cpf, quantidade_passageiros, valor_da_venda_por_cpf, cliente, emissor, cartao, valor_pago_no_cartao, pagamento_conferido, localizador, sobrenome_passageiro, data_hora_chegada, status, custo_total, venda_total],
                    values=[data_cadastro.strftime('%d/%m/%Y %H:%M'), conta, custo_por_cpf, quantidade_passageiros, valor_da_venda_por_cpf, cliente, emissor, cartao, valor_pago_no_cartao, pagamento_conferido, localizador, sobrenome_passageiro, data_hora_chegada, status, observacoes, '', custo_total, venda_total],
                    planilha=st.session_state['tipo de cadastro']
                )
