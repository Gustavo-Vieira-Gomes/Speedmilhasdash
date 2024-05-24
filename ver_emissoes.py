import streamlit as st
from spreadsheets_conn import concatenar_planliha_de_custos_faturamento
from sidebar import sidebar_ver_emissoes


def ver_emissions():
    st.markdown("""
    <style>
            .block-container {
                padding-top: 0rem;
                padding-bottom: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
    </style>
    """, unsafe_allow_html=True)

    df = concatenar_planliha_de_custos_faturamento()
    sidebar_ver_emissoes(df, st.session_state['date_init_range'])
    df_final = st.session_state['searched_df']
    st.header('Emissões Cadastradas')
    if df_final.empty:
        st.container(border=True).subheader('Nenhuma Emissão encontrada de acordo com os filtros inseridos')
    else:
        df_final.fillna({'Quem pagou as taxas': '-', 'Titular': '-', 'Login': '-', 'Senha': '-', 'Total Venda': 0, 'Total Custo': 0}, inplace=True)
        if st.session_state['nivel_acesso'] == '1':
            df_final = df_final[['Data da Emissao', 'Cliente', 'Localizador', 'Cia', 'Quantidade de Milhas', 'CPFs', 'Emitido por','Quem pagou as taxas', 'Titular', 'Login', 'Senha' ,'Total Venda', 'Status']]
        else:
            df_final = df_final[['Data da Emissao', 'Cliente', 'Localizador', 'Cia', 'Quantidade de Milhas', 'CPFs', 'Emitido por','Quem pagou as taxas', 'Titular', 'Login', 'Senha' ,'Total Venda', 'Total Custo', 'Lucro', 'Status']]
        st.container(border=True).dataframe(
            data=df_final,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Data da Emissao': st.column_config.DatetimeColumn(help='Data de Cadastro no sistema', disabled=True, required=True, format='DD/MM/YYYY HH:ss'),
                'Quantidade de Milhas': st.column_config.NumberColumn('Qntd Milhas', help='Quantidade de milhas utilizadas'),
                'CPFs': 'Nº Passageiros',
                'Total Venda': st.column_config.NumberColumn('Valor da Venda', format='R$%.2f'),
                'Total Custo': st.column_config.NumberColumn('Custo da venda', format='R$%.2f'),
                'Lucro': st.column_config.NumberColumn('Lucro', format='R$%.2f')
            }
        )