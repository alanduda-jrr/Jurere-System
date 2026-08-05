import os
from PIL import Image
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Controle de Estoque - Lanchonete", layout="wide"
)

# Arquivo simples para salvar os dados em CSV (funciona como um banco de dados local)
DB_FILE = "estoque_lanchonete.csv"
PASTA_FOTOS = "fotos_produtos"

if not os.path.exists(PASTA_FOTOS):
  os.makedirs(PASTA_FOTOS)


def carregar_dados():
  if os.path.exists(DB_FILE):
    return pd.read_csv(DB_FILE)
  else:
    # Cria a estrutura padrão se não existir
    return pd.DataFrame(columns=[
        "ID",
        "Produto",
        "Custo",
        "Preço",
        "Quantidade",
        "Estoque Mínimo",
        "Fornecedor",
        "Contato Fornecedor",
        "Foto",
    ])


df = carregar_dados()

st.title("🍔 Controle de Estoque & Bar")
st.sidebar.header("Menu de Navegação")
menu = st.sidebar.selectbox(
    "Escolha a opção", [
        "Ver Estoque / Alertas",
        "Cadastrar Produto",
        "Ajustar Estoque (Entrada/Saída)",
    ]
)

# --- 1. VER ESTOQUE E ALERTAS ---
if menu == "Ver Estoque / Alertas":
  st.header("📊 Estoque Atual")

  if df.empty:
    st.info("Nenhum produto cadastrado ainda.")
  else:
    # Alerta de estoque mínimo
    alerta_baixo = df[df["Quantidade"] <= df["Estoque Mínimo"]]
    if not alerta_baixo.empty:
      st.error(
          "⚠️ ATENÇÃO: Os produtos abaixo estão com o estoque abaixo ou igual ao"
          " limite mínimo!"
      )
      st.dataframe(
          alerta_baixo[[
              "Produto",
              "Quantidade",
              "Estoque Mínimo",
              "Fornecedor",
              "Contato Fornecedor",
          ]]
      )

    st.subheader("Lista Completa de Produtos")
    for index, row in df.iterrows():
      col1, col2, col3 = st.columns([1, 3, 2])
      with col1:
        if pd.notna(row["Foto"]) and os.path.exists(str(row["Foto"])):
          st.image(row["Foto"], width=80)
        else:
          st.write("Sem foto")
      with col2:
        st.markdown(f"**{row['Produto']}**")
        st.write(
            f"Custo: R$ {row['Custo']:.2f} | Venda: R$ {row['Preço']:.2f}"
        )
        st.write(
            f"Fornecedor: {row['Fornecedor']} ({row['Contato Fornecedor']})"
        )
      with col3:
        cor_qtd = (
            "red" if row["Quantidade"] <= row["Estoque Mínimo"] else "green"
        )
        st.markdown(
            f"Estoque: **{row['Quantidade']}** un", help="Quantidade atual"
        )
      st.divider()

# --- 2. CADASTRAR PRODUTO ---
elif menu == "Cadastrar Produto":
  st.header("➕ Cadastrar Novo Produto")

  with st.form("form_cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do Produto (Ex: Coca-Cola 350ml)")
    col1, col2 = st.columns(2)
    with col1:
      custo = st.number_input(
          "Preço de Custo (R$)", min_value=0.0, format="%.2f"
      )
      quantidade = st.number_input(
          "Quantidade Inicial", min_value=0, step=1
      )
    with col2:
      preco = st.number_input(
          "Preço de Venda (R$)", min_value=0.0, format="%.2f"
      )
      estoque_minimo = st.number_input(
          "Estoque Mínimo (Alerta)", min_value=0, step=1
      )

    st.subheader("Dados do Fornecedor")
    fornecedor = st.text_input("Nome do Fornecedor / Empresa")
    contato_fornecedor = st.text_input("Telefone ou Contato do Fornecedor")

    foto = st.file_uploader(
        "Foto do Produto", type=["png", "jpg", "jpeg"]
    )

    submit = st.form_submit_button("Salvar Produto")

    if submit:
      if nome:
        foto_path = ""
        if foto is not None:
          foto_path = os.path.join(PASTA_FOTOS, f"{nome}.jpg")
          with open(foto_path, "wb") as f:
            f.write(foto.getbuffer())

        novo_id = len(df) + 1
        novo_dado = pd.DataFrame([{
            "ID": novo_id,
            "Produto": nome,
            "Custo": custo,
            "Preço": preco,
            "Quantidade": quantidade,
            "Estoque Mínimo": estoque_minimo,
            "Fornecedor": fornecedor,
            "Contato Fornecedor": contato_fornecedor,
            "Foto": foto_path,
        }])

        df = pd.concat([df, novo_dado], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.success(f"Produto '{nome}' cadastrado com sucesso!")
      else:
        st.error("O nome do produto é obrigatório.")

# --- 3. AJUSTAR ESTOQUE ---
elif menu == "Ajustar Estoque (Entrada/Saída)":
  st.header("🔄 Ajustar Estoque Manualmente")

  if df.empty:
    st.warning("Cadastre produtos primeiro.")
  else:
    produto_escolhido = st.selectbox(
        "Selecione o Produto", df["Produto"].tolist()
    )
    produto_atual = df[df["Produto"] == produto_escolhido].iloc[0]

    st.write(f"Estoque atual de **{produto_escolhido}**: {produto_atual['Quantidade']} unidades")

    tipo_ajuste = st.radio("Tipo de Ajuste", ["Adicionar (Compra/Entrada)", "Remover (Perda/Ajuste)", "Definir Valor Exato"])
    quantidade_ajuste = st.number_input("Quantidade", min_value=0, step=1)

    if st.button("Confirmar Ajuste"):
      idx = df[df["Produto"] == produto_escolhido].index[0]
      if tipo_ajuste == "Adicionar (Compra/Entrada)":
        df.loc[idx, "Quantidade"] += quantidade_ajuste
      elif tipo_ajuste == "Remover (Perda/Ajuste)":
        df.loc[idx, "Quantidade"] = max(0, df.loc[idx, "Quantidade"] - quantidade_ajuste)
      else:
        df.loc[idx, "Quantidade"] = quantidade_ajuste

      df.to_csv(DB_FILE, index=False)
      st.success("Estoque atualizado com sucesso!")
      st.rerun()