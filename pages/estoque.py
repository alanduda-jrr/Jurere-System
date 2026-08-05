import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Gerenciamento de Estoque", page_icon="📦", layout="wide")

# Proteção de acesso
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
  st.warning("⚠️ Você precisa fazer o login na página inicial (App) para acessar o sistema.")
  st.stop()

# Barra lateral de navegação comum
st.sidebar.title(f"Usuário: {st.session_state.get('usuario', 'Convidado')}")
st.sidebar.markdown(f"Perfil: *{st.session_state.get('perfil', '')}*")
st.sidebar.divider()
if st.sidebar.button("Sair (Logout)", use_container_width=True):
  st.session_state["autenticado"] = False
  st.session_state["usuario"] = ""
  st.session_state["perfil"] = ""
  st.rerun()

ARQUIVO_ESTOQUE = "estoque.csv"


def carregar_estoque():
  if os.path.exists(ARQUIVO_ESTOQUE):
    return pd.read_csv(ARQUIVO_ESTOQUE)
  else:
    return pd.DataFrame(
        columns=[
            "ID",
            "Produto",
            "Categoria",
            "Preço (R$)",
            "Quantidade",
            "Imagem",
        ]
    )


def salvar_estoque(df):
  df.to_csv(ARQUIVO_ESTOQUE, index=False)


df_estoque = carregar_estoque()

st.title("Gerenciamento de Estoque")
st.markdown("Cadastre novos produtos, consulte o estoque atual, edite valores ou remova itens.")

aba1, aba2, aba3 = st.tabs(["Cadastrar Item", "Consultar / Editar", "Excluir Item"])

with aba1:
  st.subheader("Cadastrar Novo Produto")

  with st.form("form_cadastro", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      nome_produto = st.text_input("Nome do Produto")
      categoria = st.selectbox(
          "Categoria", ["Bebidas", "Porções", "Pratos", "Sobremesas", "Outros"]
      )
    with col2:
      preco = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f")
      quantidade = st.number_input("Quantidade em Estoque", min_value=0, step=1)

    imagem_file = st.file_uploader("Foto do Produto (Opcional)", type=["png", "jpg", "jpeg"])

    submit_cadastro = st.form_submit_button("Salvar Produto", use_container_width=True)

    if submit_cadastro:
      if not nome_produto:
        st.error("O nome do produto é obrigatório.")
      else:
        nuevo_id = int(df_estoque["ID"].max() + 1) if not df_estoque.empty and "ID" in df_estoque.columns else 1

        caminho_imagem = ""
        if imagem_file is not None:
          os.makedirs("imagens_produtos", exist_ok=True)
          caminho_imagem = os.path.join("imagens_produtos", imagem_file.name)
          with open(caminho_imagem, "wb") as f:
            f.write(imagem_file.getbuffer())

        novo_dado = pd.DataFrame(
            [{
                "ID": nuevo_id,
                "Produto": nome_produto,
                "Categoria": categoria,
                "Preço (R$)": preco,
                "Quantidade": quantidade,
                "Imagem": caminho_imagem,
            }]
        )

        df_estoque = pd.concat([df_estoque, novo_dado], ignore_index=True)
        salvar_estoque(df_estoque)
        st.success(f"Produto '{nome_produto}' cadastrado com sucesso!")
        st.rerun()

with aba2:
  st.subheader("Consultar e Editar Estoque")

  if df_estoque.empty:
    st.info("Nenhum produto cadastrado no momento.")
  else:
    df_editado = st.data_editor(
        df_estoque,
        use_container_width=True,
        num_rows="dynamic",
        key="editor_estoque",
    )

    if st.button("Salvar Alterações na Tabela", use_container_width=True):
      salvar_estoque(df_editado)
      st.success("Estoque atualizado com sucesso!")
      st.rerun()

with aba3:
  st.subheader("Excluir Produto")

  if df_estoque.empty:
    st.info("Não há produtos para excluir.")
  else:
    produto_para_excluir = st.selectbox(
        "Selecione o produto que deseja remover:",
        df_estoque["Produto"].tolist() if "Produto" in df_estoque.columns else [],
    )

    if st.button("Deletar Produto Selecionado", type="primary"):
      df_estoque = df_estoque[df_estoque["Produto"] != produto_para_excluir]
      salvar_estoque(df_estoque)
      st.success(f"O produto '{produto_para_excluir}' foi removido com sucesso!")
      st.rerun()
