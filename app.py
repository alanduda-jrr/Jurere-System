import streamlit as st
import pandas as pd
from PIL import Image
import io
import os
import base64

st.set_page_config(page_title="Controle de Estoque e PDV - Jurerê", layout="wide")

ARQUIVO_LOGO = "logo.png" 

def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_base64 = get_base64_of_bin_file(ARQUIVO_LOGO)

background_css = ""
if logo_base64:
    background_css = f"""
    background-image: linear-gradient(rgba(245, 247, 248, 0.92), rgba(245, 247, 248, 0.92)), url("data:image/png;base64,{logo_base64}");
    background-repeat: no-repeat;
    background-position: center;
    background-attachment: fixed;
    background-size: 40% auto;
    """

st.markdown(f"""
    <style>
    .stApp {{
        background-color: #F5F7F8;
        {background_css}
    }}
    </style>
    """, unsafe_allow_html=True)

ARQUIVO_ESTOQUE = "estoque.csv"
CATEGORIAS_PADRAO = ["Bebidas", "Lanches", "Porções", "Sobremesas", "Outros"]

def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        try:
            df = pd.read_csv(ARQUIVO_ESTOQUE)
            colunas_necessarias = ['ID', 'Nome', 'Categoria', 'Descrição', 'Custo', 'Quantidade', 'Caminho_Imagem']
            for col in colunas_necessarias:
                if col not in df.columns:
                    df[col] = None
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=['ID', 'Nome', 'Categoria', 'Descrição', 'Custo', 'Quantidade', 'Caminho_Imagem'])

def salvar_dados(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

if 'estoque' not in st.session_state:
    st.session_state['estoque'] = carregar_dados()

def check_password():
    def password_entered():
        if st.session_state["password"] == "1234":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Senha de acesso:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Senha de acesso:", type="password", on_change=password_entered, key="password")
        st.error("Senha incorreta.")
        return False
    else:
        return True

if check_password():
    st.title("🍔 Sistema PDV & Controle de Estoque - Jurerê")

    menu = ["PDV (Vendas / Navegação)", "Cadastrar Item", "Estoque Atual / Editar", "Movimentação"]
    escolha = st.sidebar.selectbox("Menu", menu)

    # 1. PDV (PONTO DE VENDA POR CATEGORIAS)
    if escolha == "PDV (Vendas / Navegação)":
        st.header("🛒 PDV - Frente de Caixa")
        df = st.session_state['estoque']
        
        if df.empty:
            st.info("Nenhum item cadastrado no estoque ainda. Cadastre itens no menu lateral.")
        else:
            categorias_disponiveis = sorted(df['Categoria'].dropna().unique().tolist())
            if not categorias_disponiveis:
                categorias_disponiveis = ["Geral"]
                
            categoria_selecionada = st.selectbox("📂 Selecione a Categoria:", categorias_disponiveis)
            
            itens_categoria = df[df['Categoria'] == categoria_selecionada]
            
            st.markdown("---")
            st.subheader(f"Itens da Categoria: {categoria_selecionada}")
            
            cols = st.columns(3)
            for index, row in itens_categoria.reset_index().iterrows():
                with cols[index % 3]:
                    st.markdown(f"### {row['Nome']}")
                    
                    img_path = row['Caminho_Imagem']
                    if pd.notna(img_path) and os.path.exists(str(img_path)):
                        st.image(str(img_path), width=150)
                    else:
                        st.write("*(Sem imagem)*")
                    
                    st.write(f"**Preço:** R$ {float(row['Custo']):.2f}")
                    st.write(f"**Em estoque:** {int(row['Quantidade'])} un.")
                    st.write(f"*{row['Descrição']}*")
                    
                    if st.button(f"Registrar Saída / Venda", key=f"venda_{row['ID']}"):
                        if int(row['Quantidade']) > 0:
                            idx = st.session_state['estoque'][st.session_state['estoque']['ID'] == row['ID']].index[0]
                            st.session_state['estoque'].at[idx, 'Quantidade'] = int(row['Quantidade']) - 1
                            salvar_dados(st.session_state['estoque'])
                            st.success(f"Venda de '{row['Nome']}' realizada com sucesso!")
                            st.rerun()
                        else:
                            st.error("Produto esgotado!")
                    st.markdown("---")

    # 2. CADASTRAR ITEM
    elif escolha == "Cadastrar Item":
        st.header("Cadastrar Novo Item")
        
        nome = st.text_input("Nome do Item")
        
        cat_escolhida = st.selectbox("Categoria (Padronizada)", CATEGORIAS_PADRAO)
        if cat_escolhida == "Outros":
            categoria = st.text_input("Digite o nome da nova categoria:")
        else:
            categoria = cat_escolhida
            
        descricao = st.text_area("Descrição")
        custo = st.number_input("Preço de Custo / Venda (R$)", min_value=0.0, format="%.2f")
        quantidade = st.number_input("Quantidade Inicial", min_value=0, step=1)
        
        st.subheader("Imagem do Item")
        st.info("💡 Dica: Tire o print da imagem, clique dentro da caixa tracejada abaixo e aperte **Ctrl+V**, ou arraste a imagem para dentro dela.")
        
        imagem_arquivo = st.file_uploader("Arraste a imagem ou clique para selecionar", type=["png", "jpg", "jpeg"])
        
        caminho_salvo = None
        if imagem_arquivo is not None:
            os.makedirs("imagens_produtos", exist_ok=True)
            caminho_salvo = os.path.join("imagens_produtos", imagem_arquivo.name)
            with open(caminho_salvo, "wb") as f:
                f.write(imagem_arquivo.getbuffer())
            st.image(caminho_salvo, width=200)

        if st.button("Salvar Item"):
            if nome and categoria:
                df_atual = st.session_state['estoque']
                novo_id = int(df_atual['ID'].max() + 1) if not df_atual.empty and pd.notna(df_atual['ID'].max()) else 1
                
                novo_dado = pd.DataFrame([{
                    'ID': novo_id,
                    'Nome': nome,
                    'Categoria': categoria,
                    'Descrição': descricao,
                    'Custo': custo,
                    'Quantidade': quantidade,
                    'Caminho_Imagem': caminho_salvo
                }])
                
                st.session_state['estoque'] = pd.concat([df_atual, novo_dado], ignore_index=True)
                salvar_dados(st.session_state['estoque'])
                st.success(f"Item '{nome}' cadastrado com sucesso!")
            else:
                st.warning("O Nome e a Categoria do item são obrigatórios.")

    # 3. ESTOQUE ATUAL E TELA DE EDIÇÃO
    elif escolha == "Estoque Atual / Editar":
        st.header("Estoque Atual e Gerenciamento")
        
        df = st.session_state['estoque']
        
        if df.empty:
            st.info("Nenhum item cadastrado no estoque ainda.")
        else:
            st.dataframe(df[['ID', 'Nome', 'Categoria', 'Descrição', 'Custo', 'Quantidade']], use_container_width=True)
            
            st.markdown("---")
            st.subheader("✏️ Editar um Item Existente")
            
            item_ids = df['ID'].tolist()
            item_escolhido_id = st.selectbox("Selecione o ID do item que deseja editar:", item_ids)
            
            item_atual = df.loc[df['ID'] == item_escolhido_id].iloc[0]
            
            with st.form("form_edicao"):
                novo_nome = st.text_input("Nome", value=item_atual['Nome'])
                
                cat_atual_val = item_atual['Categoria']
                idx_cat = CATEGORIAS_PADRAO.index(cat_atual_val) if cat_atual_val in CATEGORIAS_PADRAO else len(CATEGORIAS_PADRAO)-1
                nova_cat_escolhida = st.selectbox("Categoria", CATEGORIAS_PADRAO, index=idx_cat)
                if nova_cat_escolhida == "Outros":
                    nova_categoria = st.text_input("Digite a categoria:", value=cat_atual_val)
                else:
                    nova_categoria = nova_cat_escolhida
                    
                nova_desc = st.text_area("Descrição", value=item_atual['Descrição'])
                novo_custo = st.number_input("Custo (R$)", value=float(item_atual['Custo']), format="%.2f")
                nova_qtd = st.number_input("Quantidade", value=int(item_atual['Quantidade']), step=1)
                
                st.write("Imagem atual do item:")
                img_path_atual = item_atual['Caminho_Imagem']
                if pd.notna(img_path_atual) and os.path.exists(str(img_path_atual)):
                    st.image(str(img_path_atual), width=150)
                else:
                    st.write("Sem imagem cadastrada.")
                
                alterar_img = st.file_uploader("Enviar nova imagem (opcional)", type=["png", "jpg", "jpeg"])
                
                atualizar_btn = st.form_submit_button("Salvar Alterações")
                
                if atualizar_btn:
                    idx = st.session_state['estoque'][st.session_state['estoque']['ID'] == item_escolhido_id].index[0]
                    st.session_state['estoque'].at[idx, 'Nome'] = novo_nome
                    st.session_state['estoque'].at[idx, 'Categoria'] = nova_categoria
                    st.session_state['estoque'].at[idx, 'Descrição'] = nova_desc
                    st.session_state['estoque'].at[idx, 'Custo'] = novo_custo
                    st.session_state['estoque'].at[idx, 'Quantidade'] = nova_qtd
                    
                    if alterar_img is not None:
                        os.makedirs("imagens_produtos", exist_ok=True)
                        novo_caminho = os.path.join("imagens_produtos", alterar_img.name)
                        with open(novo_caminho, "wb") as f:
                            f.write(alterar_img.getbuffer())
                        st.session_state['estoque'].at[idx, 'Caminho_Imagem'] = novo_caminho
                        
                    salvar_dados(st.session_state['estoque'])
                    st.success("Item atualizado com sucesso!")
                    st.rerun()

    # 4. MOVIMENTAÇÃO
    elif escolha == "Movimentação":
        st.header("Movimentação de Estoque Manual (Entrada/Saída)")
        df = st.session_state['estoque']
        
        if df.empty:
            st.info("Nenhum item cadastrado para movimentar.")
        else:
            item_nome = st.selectbox("Selecione o Item", df['Nome'].tolist())
            tipo_mov = st.radio("Tipo de Movimentação", ["Entrada (Adicionar)", "Saída (Baixa)"])
            qtd_mov = st.number_input("Quantidade", min_value=1, step=1)
            
            if st.button("Confirmar Movimentação"):
                idx = st.session_state['estoque'][st.session_state['estoque']['Nome'] == item_nome].index[0]
                qtd_atual = int(st.session_state['estoque'].at[idx, 'Quantidade'])
                
                if tipo_mov == "Entrada (Adicionar)":
                    nova_qtd = qtd_atual + qtd_mov
                    st.session_state['estoque'].at[idx, 'Quantidade'] = nova_qtd
                    salvar_dados(st.session_state['estoque'])
                    st.success(f"Entrada realizada! Nova quantidade de {item_nome}: {nova_qtd}")
                else:
                    if qtd_atual >= qtd_mov:
                        nova_qtd = qtd_atual - qtd_mov
                        st.session_state['estoque'].at[idx, 'Quantidade'] = nova_qtd
                        salvar_dados(st.session_state['estoque'])
                        st.success(f"Baixa realizada! Nova quantidade de {item_nome}: {nova_qtd}")
                    else:
                        st.error("Quantidade em estoque insuficiente para essa baixa!")
