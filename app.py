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
    # Barra lateral limpa e profissional
    st.sidebar.title(f"Bem-vindo(a),")
    st.sidebar.markdown(f"**{st.session_state['usuario']}**")
    st.sidebar.markdown(f"Perfil: *{st.session_state['perfil']}*")
    st.sidebar.divider()
    
    st.sidebar.markdown("### 📂 Módulos do Sistema")
    
    # Menu Principal limpo em formato selectbox (substitui os botões de rádio em bolinhas)
    modulo_selecionado = st.sidebar.selectbox(
        "Selecione o Módulo",
        ["Início / Dashboard", "Estoque", "PDV (Vendas)", "Caixa"]
    )
    
    st.sidebar.divider()
    
    if st.sidebar.button("🚪 Sair (Logout)", use_container_width=True):
        st.session_state['autenticado'] = False
        st.session_state['usuario'] = ""
        st.session_state['perfil'] = ""
        st.rerun()

    # Roteamento dos Módulos com Submenus
    if modulo_selecionado == "Início / Dashboard":
        st.title("📊 Painel Inicial - Sistema Jurerê")
        st.markdown("Visão geral rápida do sistema comercial.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Status do Caixa", value="Aberto", delta="Operando")
        with col2:
            st.metric(label="Produtos Cadastrados", value="--", delta="Ver Estoque")
        with col3:
            st.metric(label="Vendas Hoje", value="R$ 0,00", delta="0 realizadas")

    elif modulo_selecionado == "Estoque":
        # Submenus de Estoque organizados internamente de forma profissional
        import importlib.util
        spec = importlib.util.spec_from_file_location("estoque", "pages/estoque.py")
        estoque_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(estoque_module)
        except Exception as e:
            st.error(f"Erro ao carregar o módulo de estoque: {e}")
            
    elif modulo_selecionado == "PDV (Vendas)":
        import importlib.util
        spec = importlib.util.spec_from_file_location("pdv", "pages/pdv.py")
        pdv_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(pdv_module)
        except Exception as e:
            st.error(f"Erro ao carregar o módulo do PDV: {e}")
            
    elif modulo_selecionado == "Caixa":
        st.title("💵 Caixa e Comandas")
        st.markdown("Gerenciamento de faturamento, comandas abertas e fechamento de caixa.")
        st.info("Módulo de Caixa em estruturação para a próxima etapa.")

# Execução principal baseada no estado de autenticação
if not st.session_state['autenticado']:
    tela_login()
else:
    painel_principal()
