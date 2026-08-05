import os
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="PDV / Vendas", page_icon="🛒", layout="wide")

ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_CAIXA = "caixa_vendas.csv"

def carregar_estoque():
  if os.path.exists(ARQUIVO_ESTOQUE):
    try:
      df = pd.read_csv(ARQUIVO_ESTOQUE)
      colunas_padrao = ["ID", "Produto", "Categoria", "Preço de Custo (R$)", "Preço de Venda (R$)", "Margem (%)", "Quantidade", "Estoque Mínimo", "Imagem"]
      for col in colunas_padrao:
        if col not in df.columns:
          df[col] = None
      return df
    except Exception:
      return pd.DataFrame(columns=["ID", "Produto", "Categoria", "Preço de Custo (R$)", "Preço de Venda (R$)", "Margem (%)", "Quantidade", "Estoque Mínimo", "Imagem"])
  return pd.DataFrame(columns=["ID", "Produto", "Categoria", "Preço de Custo (R$)", "Preço de Venda (R$)", "Margem (%)", "Quantidade", "Estoque Mínimo", "Imagem"])

def salvar_estoque(df):
  df.to_csv(ARQUIVO_ESTOQUE, index=False)

def registrar_venda_caixa(descricao, valor, forma_pagamento):
  try:
    if os.path.exists(ARQUIVO_CAIXA):
      df_caixa = pd.read_csv(ARQUIVO_CAIXA)
    else:
      df_caixa = pd.DataFrame(columns=["ID_Venda", "Tipo", "Descricao", "Valor", "Forma_Pagamento", "Horario"])
    
    novo_id = int(df_caixa["ID_Venda"].max() + 1) if not df_caixa.empty and "ID_Venda" in df_caixa.columns and pd.notna(df_caixa["ID_Venda"].max()) else 1
    
    novo_registro = pd.DataFrame([{
        "ID_Venda": novo_id,
        "Tipo": "Venda",
        "Descricao": descricao,
        "Valor": valor,
        "Forma_Pagamento": forma_pagamento,
        "Horario": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    
    df_caixa = pd.concat([df_caixa, novo_registro], ignore_index=True)
    df_caixa.to_csv(ARQUIVO_CAIXA, index=False)
  except Exception as e:
    st.error(f"Erro ao registrar caixa: {e}")

if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
  st.warning("⚠️ Você precisa fazer o login na página inicial para acessar o sistema.")
  st.stop()

st.title("🛒 Frente de Caixa (PDV)")
st.markdown("Realize vendas e dê baixa automática no estoque.")

df_estoque = carregar_estoque()

if df_estoque.empty or "Produto" not in df_estoque.columns or df_estoque["Produto"].dropna().empty:
  st.info("⚠️ Nenhum produto cadastrado no estoque para iniciar as vendas.")
else:
  produtos_disponiveis = df_estoque["Produto"].dropna().tolist()
  produto_escolhido = st.selectbox("Selecione o Produto", produtos_disponiveis)
  
  dados_prod = df_estoque[df_estoque["Produto"] == produto_escolhido].iloc[0]
  preco_venda = float(dados_prod["Preço de Venda (R$)"]) if pd.notna(dados_prod["Preço de Venda (R$)"]) else 0.0
  estoque_atual = int(dados_prod["Quantidade"]) if pd.notna(dados_prod["Quantidade"]) else 0
  
  st.markdown(f"💰 **Preço Unitário:** R$ {preco_venda:.2f}")
  st.markdown(f"📦 **Estoque Disponível:** {estoque_atual} unidades")
  
  quantidade_comprar = st.number_input("Quantidade", min_value=1, max_value=max(1, estoque_atual), value=1, step=1)
  forma_pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito"])

  if st.button("Finalizar Venda e Dar Baixa", type="primary", use_container_width=True):
    if estoque_atual < quantidade_comprar:
      st.error("❌ Quantidade superior ao estoque disponível!")
    else:
      idx = df_estoque[df_estoque["Produto"] == produto_escolhido].index[0]
      df_estoque.loc[idx, "Quantidade"] = estoque_atual - quantidade_comprar
      salvar_estoque(df_estoque)
      
      valor_total = preco_venda * quantidade_comprar
      descricao_venda = f"{quantidade_comprar}x {produto_escolhido}"
      registrar_venda_caixa(descricao_venda, valor_total, forma_pgto)
      
      st.success(f"✅ Venda realizada com sucesso! Estoque atualizado.")
      st.rerun()
