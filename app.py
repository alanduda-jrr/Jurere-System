import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sistema Jurerê",
    page_icon="🔐",
    layout="wide"
)

# Inicializa as variáveis de controle de sessão
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = ""
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = ""

# Base simples de usuários simulada
USUARIOS = {
    "admin": {"senha": "123", "perfil": "Administrador", "nome": "Administrador do Sistema"},
    "operador": {"senha": "123", "perfil": "Operador", "nome": "Funcionário Balcão"}
}

def tela_login():
    st.markdown("<h2 style='text-align: center;'>🔐 Login - Sistema Jurerê</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Insira suas credenciais para acessar o sistema.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        with st.form("form_login"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                if username in USUARIOS and USUARIOS[username]["senha"] == password:
                    st.session_state['autenticado'] = True
                    st.session_state['usuario'] = USUARIOS[username]["nome"]
                    st.session_state['perfil'] = USUARIOS[username]["perfil"]
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

def painel_principal():
    # Barra lateral com menu de navegação explícito
    st.sidebar.title(f"Bem-vindo(a),")
    st.sidebar.markdown(f"**{st.session_state['usuario']}**")
    st.sidebar.markdown(f"Perfil: *{st.session_state['perfil']}*")
    st.sidebar.divider()
    
    st.sidebar.markdown("### 📂 Menu do Sistema")
    
    # Links diretos para as páginas na pasta pages/
    st.sidebar.page_link("app.py", label="Início / Dashboard", icon="🏠")
    st.sidebar.page_link("pages/estoque.py", label="Gerenciar Estoque", icon="📦")
    st.sidebar.page_link("pages/pdv.py", label="Frente de Caixa (PDV)", icon="🛒")
    
    st.sidebar.divider()
    
    if st.sidebar.button("🚪 Sair (Logout)", use_container_width=True):
        st.session_state['autenticado'] = False
        st.session_state['usuario'] = ""
        st.session_state['perfil'] = ""
        st.rerun()

    # Conteúdo da Página Inicial (Home / Dashboard)
    st.title("📊 Painel Inicial - Sistema Jurerê")
    st.markdown("Visão geral rápida do sistema comercial.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Status do Caixa", value="Aberto", delta="Operando")
    with col2:
        st.metric(label="Produtos Cadastrados", value="--", delta="Ver Estoque")
    with col3:
        st.metric(label="Vendas Hoje", value="R$ 0,00", delta="0 realizadas")

    st.divider()
    st.markdown("### Atalhos Rápidos")
    st.markdown("""
    - Utilize o menu na **barra lateral à esquerda** para navegar entre as seções.
    - Vá para **Gerenciar Estoque** para cadastrar ou gerenciar produtos e preços.
    - Vá para **Frente de Caixa (PDV)** para registrar novas vendas.
    """)

# Execução principal baseada no estado de autenticação
if not st.session_state['autenticado']:
    tela_login()
else:
    painel_principal()
