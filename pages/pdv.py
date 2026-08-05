import os
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="PDV - Frente de Caixa e Comandas", page_icon="🛒", layout="wide")

st.markdown("""
<style>
    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        gap: 0.2rem !important;
    }
    div[data-testid="stContainer"] {
        padding-top: 5px !important;
        padding-bottom: 5px !important;
    }
    .card-img-box {
        width: 100%;
        height: 110px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 0px !important;
        margin-bottom: 0px !important;
    }
    .card-img-box img {
        max-height: 110px !important;
        max-width: 100% !important;
        width: auto !important;
        object-fit: contain !important;
    }
</style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
  st.warning("⚠️ Você precisa fazer o login na página inicial para acessar o sistema.")
  st.stop()

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
    
    from datetime import datetime
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

@st.dialog("➕ Adicionar à Comanda / Venda")
def modal_adicionar_comanda(row_id):
  df = carregar_estoque()
  row_data = df[df["ID"] == row_id]
  if row_data.empty:
    st.error("Item não encontrado.")
    return
  
  row = row_data.iloc[0]
  produto_nome = str(row['Produto'])
  preco_venda = float(row['Preço de Venda (R$)']) if pd.notna(row['Preço de Venda (R$)']) else 0.0
  estoque_atual = int(row['Quantidade']) if pd.notna(row['Quantidade']) else 0

  st.markdown(f"**Produto:** {produto_nome}")
  st.markdown(f"💰 **Preço Unitário:** R$ {preco_venda:.2f}")
  st.markdown(f"📦 **Disponível em Estoque:** {estoque_atual} un.")

  with st.form(key=f"form_comanda_{row_id}"):
    qtd_comprar = st.number_input("Quantidade", min_value=1, max_value=max(1, estoque_atual), value=1, step=1)
    forma_pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito"])
    
    confirmar = st.form_submit_button("🛒 Confirmar Lançamento", use_container_width=True)

    if confirmar:
      if estoque_atual < qtd_comprar:
        st.error("❌ Quantidade superior ao estoque disponível!")
      else:
        idx_linha = df[df["ID"] == row_id].index[0]
        df.loc[idx_linha, "Quantidade"] = estoque_atual - qtd_comprar
        salvar_estoque(df)

        valor_total = preco_venda * qtd_comprar
        descricao_venda = f"{qtd_comprar}x {produto_nome}"
        registrar_venda_caixa(descricao_venda, valor_total, forma_pgto)

        st.session_state["msg_pdv"] = f"✅ {descricao_venda} lançado com sucesso!"
        st.rerun()

st.title("🛒 PDV - Frente de Caixa e Comandas")
st.markdown("Realize vendas diretas no balcão ou lance itens em comandas abertas.")

if "msg_pdv" in st.session_state:
  st.success(st.session_state["msg_pdv"])
  del st.session_state["msg_pdv"]

df_estoque = carregar_estoque()

if df_estoque.empty or df_estoque["Produto"].dropna().empty:
  st.info("Nenhum produto cadastrado no estoque.")
else:
  df_estoque["Quantidade"] = pd.to_numeric(df_estoque["Quantidade"], errors="coerce").fillna(0)
  
  # Filtra apenas itens com estoque maior que 0 e ordena alfabeticamente pelo nome do produto
  df_disponivel = df_estoque[df_estoque["Quantidade"] > 0].copy()
  df_disponivel = df_disponivel.sort_values(by="Produto", ascending=True)

  col_f1, col_f2 = st.columns([2, 1])
  with col_f1:
    termo_busca = st.text_input("🔍 Pesquisa:", placeholder="Filtrar produto...", label_visibility="collapsed")
  with col_f2:
    categorias_disponiveis = ["Todas"] + sorted(list(df_disponivel["Categoria"].dropna().unique()))
    cat_filtro = st.selectbox("Categoria", categorias_disponiveis, label_visibility="collapsed")

  if termo_busca:
    df_disponivel = df_disponivel[df_disponivel["Produto"].str.contains(termo_busca, case=False, na=False)]
  if cat_filtro != "Todas":
    df_disponivel = df_disponivel[df_disponivel["Categoria"] == cat_filtro]

  st.divider()

  if df_disponivel.empty:
    st.info("Nenhum produto disponível em estoque com os filtros selecionados.")
  else:
    cols = st.columns(5)
    for idx, row in df_disponivel.reset_index().iterrows():
      with cols[idx % 5]:
        with st.container(border=True):
          caminho_img = str(row["Imagem"])
          if caminho_img and caminho_img != "nan" and os.path.exists(caminho_img):
            st.markdown(f"<div class='card-img-box'>", unsafe_allow_html=True)
            st.image(caminho_img, use_container_width=False)
            st.markdown("</div>", unsafe_allow_html=True)
          else:
            st.markdown("<div class='card-img-box' style='color: gray; font-size: 11px;'>Sem foto</div>", unsafe_allow_html=True)

          produto_nome = str(row['Produto'])
          venda = float(row['Preço de Venda (R$)']) if pd.notna(row['Preço de Venda (R$)']) else 0.0
          qtd = int(row['Quantidade'])

          card_html = f"""
          <div style="font-size: 11px; line-height: 1.3; margin-bottom: 2px; text-align: center;">
            <b style="font-size: 12px; display: block; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #333;" title="{produto_nome}">{produto_nome}</b>
            <div style="background-color: #d4edda; color: #28a745; padding: 3px 6px; border-radius: 4px; margin-bottom: 6px; font-weight: bold;">📦 Estoque: {qtd} un.</div>
            <div style="border-top: 1px solid #eee; padding-top: 4px; color: #333; font-size: 12px;">
              <div>Venda: <b>R$ {venda:.2f}</b></div>
            </div>
          </div>
          """
          st.markdown(card_html, unsafe_allow_html=True)
          
          if st.button("➕ Adicionar", key=f"btn_add_{row['ID']}", use_container_width=True, type="primary"):
            modal_adicionar_comanda(row['ID'])
