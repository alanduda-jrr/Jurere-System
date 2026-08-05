import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PDV - Vendas", page_icon="🛒", layout="wide")

# Proteção de acesso
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
  st.warning("⚠️ Você precisa fazer o login na página inicial (App) para acessar o sistema.")
  st.stop()

# Barra lateral
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
    return pd.DataFrame(columns=["ID", "Produto", "Categoria", "Preço (R$)", "Quantidade", "Imagem"])


def salvar_estoque(df):
  df.to_csv(ARQUIVO_ESTOQUE, index=False)


df_estoque = carregar_estoque()

st.title("🛒 PDV - Frente de Caixa e Vendas")
st.markdown("Realize vendas de balcão ou lance pedidos por mesa/comanda.")

if df_estoque.empty:
  st.info("Nenhum produto cadastrado no estoque. Cadastre itens na página de Estoque primeiro.")
else:
  # Filtro por categoria
  categorias = ["Todas"] + list(df_estoque["Categoria"].dropna().unique())
  cat_selecionada = st.selectbox("Filtrar por Categoria", categorias)

  if cat_selecionada != "Todas":
    df_filtrado = df_estoque[df_estoque["Categoria"] == cat_selecionada]
  else:
    df_filtrado = df_estoque

  st.divider()

  # Exibição dos produtos em colunas estilo catálogo
  cols = st.columns(3)
  for idx, row in df_filtrado.reset_index().iterrows():
    with cols[idx % 3]:
      st.markdown(f"### {row['Produto']}")
      st.markdown(f"**Categoria:** {row['Categoria']}")
      st.markdown(f"**Preço:** R$ {row['Preço (R$)']:.2f}")
      st.markdown(f"**Disponível:** {row['Quantidade']} un.")

      # Botão de venda rápida
      if st.button(f"Vender: {row['Produto']}", key=f"venda_{row['ID']}"):
        if row["Quantidade"] > 0:
          # Atualiza a quantidade no DataFrame local
          indice_original = df_estoque[df_estoque["ID"] == row["ID"]].index[0]
          df_estoque.at[indice_original, "Quantidade"] -= 1
          salvar_estoque(df_estoque)
          st.success(f"Venda de '{row['Produto']}' realizada com sucesso!")
          st.rerun()
        else:
          st.error("Produto esgotado no estoque!")

      st.markdown("---")
