import os
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Gerenciamento de Estoque", page_icon="📦", layout="wide")

if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
  st.warning("⚠️ Você precisa fazer o login na página inicial (App) para acessar o sistema.")
  st.stop()

st.sidebar.title(f"Usuário: {st.session_state.get('usuario', 'Convidado')}")
st.sidebar.markdown(f"Perfil: *{st.session_state.get('perfil', '')}*")
st.sidebar.divider()
if st.sidebar.button("Sair (Logout)", use_container_width=True):
  st.session_state["autenticado"] = False
  st.session_state["usuario"] = ""
  st.session_state["perfil"] = ""
  st.rerun()

ARQUIVO_ESTOQUE = "estoque.csv"
PASTA_IMAGENS = "imagens_produtos"

def carregar_estoque():
  if os.path.exists(ARQUIVO_ESTOQUE):
    df = pd.read_csv(ARQUIVO_ESTOQUE)
    # Padroniza caso venha de versões anteriores
    colunas_padrao = ["ID", "Produto", "Categoria", "Preço de Custo (R$)", "Preço de Venda (R$)", "Margem (%)", "Quantidade", "Estoque Mínimo", "Imagem"]
    for col in colunas_padrao:
      if col not in df.columns:
        df[col] = None
    return df[colunas_padrao]
  else:
    return pd.DataFrame(
        columns=[
            "ID",
            "Produto",
            "Categoria",
            "Preço de Custo (R$)",
            "Preço de Venda (R$)",
            "Margem (%)",
            "Quantidade",
            "Estoque Mínimo",
            "Imagem",
        ]
    )

def salvar_estoque(df):
  df.to_csv(ARQUIVO_ESTOQUE, index=False)

def redimensionar_e_salvar_imagem(imagem_file, nome_produto):
  try:
    os.makedirs(PASTA_IMAGENS, exist_ok=True)
    img = Image.open(imagem_file)
    img.thumbnail((400, 400))
    nome_arquivo_limpo = "".join(c for c in nome_produto if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    extensao = os.path.splitext(imagem_file.name)[1].lower()
    if not extensao:
      extensao = ".png"
    caminho_completo = os.path.join(PASTA_IMAGENS, f"{nome_arquivo_limpo}{extensao}")
    img.save(caminho_completo)
    return caminho_completo
  except Exception as e:
    return ""

df_estoque = carregar_estoque()

st.title("📦 Gerenciamento de Estoque")
st.markdown("Cadastre, consulte e gerencie os itens do estabelecimento no novo padrão unificado.")

aba1, aba2, aba3 = st.tabs(["➕ Cadastrar Novo Item", "📋 Consultar / Estoque Atual", "🗑️ Excluir Item"])

with aba1:
  st.subheader("Cadastro de Produto")
  with st.form("form_cadastro_avancado", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
      nome_produto = st.text_input("Nome do Produto *")
      categoria = st.selectbox("Categoria *", ["Bebidas", "Porções", "Pratos Principais", "Sobremesas", "Insumos", "Outros"])
      preco_custo = st.number_input("Preço de Custo (R$) *", min_value=0.0, format="%.2f")
      preco_venda = st.number_input("Preço de Venda (R$) *", min_value=0.0, format="%.2f")

    with col2:
      quantidade = st.number_input("Quantidade Inicial / Atual *", min_value=0, step=1)
      estoque_minimo = st.number_input("Quantidade Mínima (Alerta) *", min_value=0, step=1, value=5)
      imagem_file = st.file_uploader("Foto do Produto (Opcional)", type=["png", "jpg", "jpeg"])

    margem_calc = 0.0
    if preco_custo > 0 and preco_venda > 0:
      margem_calc = ((preco_venda - preco_custo) / preco_venda) * 100

    st.markdown(f"ℹ️ **Margem de Lucro Estimada:** `{margem_calc:.2f}%`")

    submit_cadastro = st.form_submit_button("Salvar Produto no Estoque", use_container_width=True)

    if submit_cadastro:
      if not nome_produto or preco_venda <= 0:
        st.error("⚠️ Preencha os campos obrigatórios (*).")
      else:
        novo_id = int(df_estoque["ID"].max() + 1) if not df_estoque.empty and pd.notna(df_estoque["ID"].max()) else 1
        caminho_imagem = redimensionar_e_salvar_imagem(imagem_file, nome_produto) if imagem_file else ""

        novo_dado = pd.DataFrame([{
            "ID": novo_id,
            "Produto": nome_produto,
            "Categoria": categoria,
            "Preço de Custo (R$)": preco_custo,
            "Preço de Venda (R$)": preco_venda,
            "Margem (%)": round(margem_calc, 2),
            "Quantidade": quantidade,
            "Estoque Mínimo": estoque_minimo,
            "Imagem": caminho_imagem,
        }])

        df_estoque = pd.concat([df_estoque, novo_dado], ignore_index=True)
        salvar_estoque(df_estoque)
        st.success("✅ Produto cadastrado com sucesso!")
        st.rerun()

with aba2:
  st.subheader("Estoque Atual e Alertas")
  if df_estoque.empty:
    st.info("Nenhum produto cadastrado.")
  else:
    df_editado = st.data_editor(df_estoque, use_container_width=True, num_rows="dynamic", key="editor_estoque_avancado")
    if st.button("💾 Salvar Alterações", use_container_width=True):
      if "Preço de Custo (R$)" in df_editado.columns and "Preço de Venda (R$)" in df_editado.columns:
        df_editado["Margem (%)"] = df_editado.apply(
            lambda r: round(((r["Preço de Venda (R$)"] - r["Preço de Custo (R$)"]) / r["Preço de Venda (R$)"]) * 100, 2) 
            if r["Preço de Venda (R$)"] > 0 else 0.0, axis=1
        )
      salvar_estoque(df_editado)
      st.success("✅ Atualizado com sucesso!")
      st.rerun()

with aba3:
  st.subheader("Excluir Produto")
  if df_estoque.empty:
    st.info("Nenhum produto para excluir.")
  else:
    produto_para_excluir = st.selectbox("Selecione o produto:", df_estoque["Produto"].dropna().tolist())
    if st.button("🗑️ Deletar", type="primary"):
      df_estoque = df_estoque[df_estoque["Produto"] != produto_para_excluir]
      salvar_estoque(df_estoque)
      st.success("Removido com sucesso!")
      st.rerun()
