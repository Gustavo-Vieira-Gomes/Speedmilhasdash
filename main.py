import streamlit as st
import streamlit_authenticator as st_auth
from Visão_Geral import visao_geral
from cadastrar_emissao import formulario_de_cadastro
from ver_emissoes import ver_emissions
import datetime
from spreadsheets_conn import *
import dotenv

dotenv.load_dotenv()

cria_secrets_file()

COOKIE_EXPIRY_DAYS = 180

def configure_page():
    st.set_page_config('Speedmilhas Dashboard', layout='wide')

def authenticate_user():
    st.session_state['usuarios'] = pesquisar_logins()
    authenticator = st_auth.Authenticate(
        credentials=st.session_state['usuarios'],
        cookie_name='speed_app_cookie',
        cookie_expiry_days=COOKIE_EXPIRY_DAYS,
        cookie_key='random'
    )
    return authenticator.login(fields={
        'Form name': 'Login',
        'Username': 'Username',
        'Password': 'Password',
        'Login': 'Login'
    }), authenticator

def load_data():
    st.session_state['df'] = concatenar_planliha_de_custos_faturamento()

def initialize_session_state():
    if 'date_init_range' not in st.session_state:
        st.session_state['date_init_range'] = (datetime.date.today(), datetime.datetime.today() + datetime.timedelta(1))

def handle_user_navigation(nivel_acesso):
    if nivel_acesso == '1':
        handle_admin_navigation()
    elif nivel_acesso == '2':
        handle_user_navigation_2()

def handle_admin_navigation():
    page = st.sidebar.selectbox('Escolha a página', options=['Cadastrar Emissão', 'Ver Emissão'])
    st.sidebar.divider()
    if page == 'Cadastrar Emissão':
        formulario_de_cadastro()
    elif page == 'Ver Emissão':
        ver_emissions()

def handle_user_navigation_2():
    page = st.sidebar.selectbox('Escolha a página', options=['Visão Geral', 'Cadastrar Emissão', 'Ver Emissão'])
    st.sidebar.divider()
    if page == 'Visão Geral':
        visao_geral()
    elif page== 'Cadastrar Emissão':
        formulario_de_cadastro()
    elif page == 'Ver Emissão':
        ver_emissions()

def main():
    configure_page()
    info_login, authenticator = authenticate_user()
    name, authentication_status, username = info_login

    if authentication_status:
        load_data()
        nivel_acesso = st.session_state['usuarios']['usernames'][st.session_state['username']]['Acesso']
        st.session_state['nivel_acesso'] = nivel_acesso
        initialize_session_state()
        handle_user_navigation(nivel_acesso)
        authenticator.logout('logout', location='sidebar', key='logout_button')

    elif authentication_status == False:
        st.error('Usuário/Senha incorretos!')
    
    elif authentication_status == None:
        st.warning('Informe user/senha')

if __name__ == "__main__":
    main()
