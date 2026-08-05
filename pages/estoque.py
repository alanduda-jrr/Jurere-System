import os
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Gerenciamento de Estoque", page_icon="📦", layout="wide")

# CSS agressivo para eliminar o espaçamento interno superior dos containers no Streamlit
st.markdown("""
<style>
    /* Remove o padding interno superior do container do Streamlit */
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
ARQUIVO_CAIXA = "caixa_vendas.csv"
PASTA_IMAGENS = "imagens_produtos"

LISTA_CATEGORIAS = [
    "Agua",
    "Refrigerantes",
    "Cervejas",
    "Drinks",
    "Isotonicos e Eneréticos",
    "Porções",
    "Assados e Fritos",
    "Sobremesas",
    "Snacks/Aperitivos"
]

def carregar_estoque():
  if os.path.exists(ARQUIVO_ESTOQUE):
    df = pd.read_csv(ARQUIVO_ESTOQUE)
    colunas_padrao = ["ID", "Produto", "Categoria", "Preço de Custo (R$)", "Preço de Venda (R$)", "Margem (%)", "Quantidade", "Estoque Mínimo", "Imagem"]
    for col in colunas_padrao:
      if col not in df.columns:
        df[col] = None
    return df[colunas_padrao]
  else:
    return pd.DataFrame(columns=["ID", "Produto", "Categoria", "Preço de Custo (R$)", "Preço de Venda (R$)", "Margem (%)", "Quantidade", "Estoque Mínimo", "Imagem"])

def salvar_estoque(df):
  df.to_csv(ARQUIVO_ESTOQUE, index=False)

def carregar_vendas():
  if os.path.exists(ARQUIVO_CAIXA):
    return pd.read_csv(ARQUIVO_CAIXA)
  return pd.DataFrame(columns=["ID_Venda", "Tipo", "Descricao", "Valor", "Forma_Pagamento", "Horario"])

def redimensionar_e_padronizar_imagem(imagem_file, nome_produto):
  """Processa a imagem cortando bordas excedentes e ajustando de forma otimizada."""
  try:
    os.makedirs(PASTA_IMAGENS, exist_ok=True)
    img = Image.open(imagem_file)
    if img.mode in ("RGBA", "P"):
      background = Image.new("RGB", img.size, (255, 255, 255))
      if img.mode == "RGBA":
        background.paste(img, mask=img.split()[3])
      else:
        background.paste(img)
      img = background

    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
    
    nome_arquivo_limpo = "".join(c for c in nome_produto if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    caminho_completo = os.path.join(PASTA_IMAGENS, f"{nome_arquivo_limpo}.jpg")
    img.save(caminho_completo, "JPEG", quality=90)
    return caminho_completo
  except Exception as e:
    return ""

df_estoque = carregar_estoque()
df_caixa = carregar_vendas()

@st.dialog("✏️ Editar Produto")
def modal_editar(row_id):
  df = carregar_estoque()
  row_data = df[df["ID"] == row_id]
  if row_data.empty:
    st.error("Item não encontrado.")
    return
  
  row = row_data.iloc[0]
  
  produto_nome = str(row['Produto'])
  custo = float(row['Preço de Custo (R$)']) if pd.notna(row['Preço de Custo (R$)']) else 0.0
  venda = float(row['Preço de Venda (R$)']) if pd.notna(row['Preço de Venda (R$)']) else 0.0
  qtd = int(row['Quantidade']) if pd.notna(row['Quantidade']) else 0
  min_q = int(row['Estoque Mínimo']) if pd.notna(row['Estoque Mínimo']) else 0
  cat_atual = str(row['Categoria'])

  with st.form(key=f"form_modal_{row_id}"):
    novo_nome = st.text_input("Nome", value=produto_nome)
    
    cat_index = LISTA_CATEGORIAS.index(cat_atual) if cat_atual in LISTA_CATEGORIAS else 0
    nova_cat = st.selectbox("Categoria", LISTA_CATEGORIAS, index=cat_index)

    novo_custo = st.number_input("Preço Custo", value=float(custo), min_value=0.0, format="%.2f")
    novo_venda = st.number_input("Preço Venda", value=float(venda), min_value=0.0, format="%.2f")
    nova_qtd = st.number_input("Quantidade", value=int(qtd), min_value=0, step=1)
    novo_min = st.number_input("Estoque Mínimo", value=int(min_q), min_value=0, step=1)
    nova_img = st.file_uploader("Nova Foto (Opcional)", type=["png", "jpg", "jpeg"])

    salvar_alteracao = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)

    if salvar_alteracao:
      nova_margem = ((novo_venda - novo_custo) / novo_venda * 100) if novo_venda > 0 else 0.0
      caminho_final = str(row["Imagem"])
      if nova_img:
        caminho_final = redimensionar_e_padronizar_imagem(nova_img, novo_nome)

      idx_linha = df[df["ID"] == row_id].index
      df.loc[idx_linha, "Produto"] = novo_nome
      df.loc[idx_linha, "Categoria"] = nova_cat
      df.loc[idx_linha, "Preço de Custo (R$)"] = novo_custo
      df.loc[idx_linha, "Preço de Venda (R$)"] = novo_venda
      df.loc[idx_linha, "Margem (%)"] = round(nova_margem, 2)
      df.loc[idx_linha, "Quantidade"] = nova_qtd
      df.loc[idx_linha, "Estoque Mínimo"] = novo_min
      df.loc[idx_linha, "Imagem"] = caminho_final

      salvar_estoque(df)
      
      st.session_state["msg_sucesso"] = f"✅ Alteração realizada com sucesso no produto '{novo_nome}'!"
      st.session_state["aba_ativa"] = "galeria"
      st.rerun()

st.title("📦 Gerenciamento de Estoque")
st.markdown("Cadastro e edição de itens / Movimentação de estoque")

if "msg_sucesso" in st.session_state:
  st.success(st.session_state["msg_sucesso"])
  del st.session_state["msg_sucesso"]

if "aba_ativa" not in st.session_state:
  st.session_state["aba_ativa"] = "galeria"

col_b1, col_b2, col_vazio = st.columns([1.5, 1.8, 6.7])
with col_b1:
  btn_cad = st.button("➕ CADASTRAR", use_container_width=True, type="primary" if st.session_state["aba_ativa"] == "cadastro" else "secondary")
  if btn_cad:
    st.session_state["aba_ativa"] = "cadastro"
    st.rerun()
with col_b2:
  btn_mov = st.button("📦 MOVIMENTAÇÃO", use_container_width=True, type="primary" if st.session_state["aba_ativa"] == "galeria" else "secondary")
  if btn_mov:
    st.session_state["aba_ativa"] = "galeria"
    st.rerun()

st.divider()

if st.session_state["aba_ativa"] == "cadastro":
  st.subheader("Cadastro de Produto")
  with st.form("form_cadastro_avancado", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
      nome_produto = st.text_input("Nome do Produto *")
      categoria = st.selectbox("Categoria *", LISTA_CATEGORIAS)
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
        df_estoque = carregar_estoque()
        novo_id = int(df_estoque["ID"].max() + 1) if not df_estoque.empty and pd.notna(df_estoque["ID"].max()) else 1
        caminho_imagem = redimensionar_e_padronizar_imagem(imagem_file, nome_produto) if imagem_file else ""

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
        st.session_state["msg_sucesso"] = "✅ Produto cadastrado com sucesso!"
        st.session_state["aba_ativa"] = "galeria"
        st.rerun()

else:
  st.subheader("Galeria Compacta")

  df_estoque = carregar_estoque()
  if df_estoque.empty or df_estoque["Produto"].dropna().empty:
    st.info("Nenhum produto cadastrado no momento.")
  else:
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
      termo_busca = st.text_input("🔍 Pesquisa inteligente:", placeholder="Digite para filtrar instantaneamente (ex: HEIN)...", label_visibility="collapsed")
    with col_f2:
      categorias_disponiveis = ["Todas as categorias"] + list(df_estoque["Categoria"].dropna().unique())
      cat_filtro = st.selectbox("Categoria", categorias_disponiveis, label_visibility="collapsed")

    df_galeria = df_estoque.copy()
    if termo_busca:
      df_galeria = df_galeria[df_galeria["Produto"].str.contains(termo_busca, case=False, na=False)]
    
    if cat_filtro != "Todas as categorias":
      df_galeria = df_galeria[df_galeria["Categoria"] == cat_filtro]

    st.divider()

    if df_galeria.empty:
      st.info("Nenhum produto encontrado com os filtros informados.")
    else:
      cols = st.columns(5)
      
      for idx, row in df_galeria.reset_index().iterrows():
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
            custo = float(row['Preço de Custo (R$)']) if pd.notna(row['Preço de Custo (R$)']) else 0.0
            venda = float(row['Preço de Venda (R$)']) if pd.notna(row['Preço de Venda (R$)']) else 0.0
            margem = float(row['Margem (%)']) if pd.notna(row['Margem (%)']) else 0.0
            qtd = int(row['Quantidade']) if pd.notna(row['Quantidade']) else 0
            min_q = int(row['Estoque Mínimo']) if pd.notna(row['Estoque Mínimo']) else 0

            vendas_semana = 0
            if not df_caixa.empty and "Descricao" in df_caixa.columns:
              nome_prod = produto_nome.lower()
              for _, v_row in df_caixa.iterrows():
                if nome_prod in str(v_row["Descricao"]).lower():
                  vendas_semana += 1

            cor_estoque = "#d9534f" if qtd <= min_q else "#28a745"
            bg_estoque = "#f8d7da" if qtd <= min_q else "#d4edda"
            alerta_txt = " (Baixo!)" if qtd <= min_q else ""

            card_html = f"""
            <div style="font-size: 11px; line-height: 1.3; margin-bottom: 2px; text-align: center;">
              <b style="font-size: 12px; display: block; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #333;" title="{produto_nome}">{produto_nome}</b>
              
              <div style="background-color: {bg_estoque}; color: {cor_estoque}; padding: 3px 6px; border-radius: 4px; margin-bottom: 3px; font-weight: bold; text-align: center;">
                📦 Estoque: {qtd} un.{alerta_txt}
              </div>
              
              <div style="background-color: #e2f0d9; color: #276a16; padding: 3px 6px; border-radius: 4px; margin-bottom: 6px; font-weight: bold; text-align: center;">
                📈 Vendas (7d): {vendas_semana} un.
              </div>

              <div style="border-top: 1px solid #eee; padding-top: 4px; color: #555;">
                <div>Custo: R$ {custo:.2f} | Venda: R$ {venda:.2f}</div>
                <div>Margem: <b>{margem:.1f}%</b></div>
              </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            if st.button("✏️ Alterar", key=f"btn_alt_{row['ID']}", use_container_width=True):
              modal_editar(row['ID'])
