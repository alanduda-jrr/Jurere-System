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
ARQUIVO_CAIXA = "caixa_vendas.csv"
PASTA_IMAGENS = "imagens_produtos"

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

def redimensionar_e_salvar_imagem(imagem_file, nome_produto):
  try:
    os.makedirs(PASTA_IMAGENS, exist_ok=True)
    img = Image.open(imagem_file)
    img.thumbnail((250, 250))
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
df_caixa = carregar_vendas()

st.title("📦 Gerenciamento de Estoque")
st.markdown("Catálogo compacto em grade de 5 colunas com opção de edição e exclusão detalhada.")

aba1, aba2 = st.tabs(["➕ Cadastrar Novo Item", "🖼️ Mini Galeria de Estoque"])

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
  st.subheader("Galeria Compacta")

  if df_estoque.empty or df_estoque["Produto"].dropna().empty:
    st.info("Nenhum produto cadastrado no momento.")
  else:
    categorias_disponiveis = ["Todas"] + list(df_estoque["Categoria"].dropna().unique())
    cat_filtro = st.selectbox("Filtrar por Categoria:", categorias_disponiveis)

    if cat_filtro != "Todas":
      df_galeria = df_estoque[df_estoque["Categoria"] == cat_filtro]
    else:
      df_galeria = df_estoque

    st.divider()

    # Grade estrita de 5 colunas por linha
    cols = st.columns(5)
    
    for idx, row in df_galeria.reset_index().iterrows():
      with cols[idx % 5]:
        with st.container(border=True):
          caminho_img = str(row["Imagem"])
          if caminho_img and caminho_img != "nan" and os.path.exists(caminho_img):
            st.image(caminho_img, use_container_width=True)
          else:
            st.markdown("<div style='text-align: center; color: gray; font-size: 11px; padding: 15px 0;'>Sem foto</div>", unsafe_allow_html=True)

          produto_nome = str(row['Produto'])
          custo = float(row['Preço de Custo (R$)']) if pd.notna(row['Preço de Custo (R$)']) else 0.0
          venda = float(row['Preço de Venda (R$)']) if pd.notna(row['Preço de Venda (R$)']) else 0.0
          margem = float(row['Margem (%)']) if pd.notna(row['Margem (%)']) else 0.0
          qtd = int(row['Quantidade']) if pd.notna(row['Quantidade']) else 0
          min_q = int(row['Estoque Mínimo']) if pd.notna(row['Estoque Mínimo']) else 0
          cat_atual = str(row['Categoria'])

          # Vendas na última semana
          vendas_semana = 0
          if not df_caixa.empty and "Descricao" in df_caixa.columns:
            nome_prod = produto_nome.lower()
            for _, v_row in df_caixa.iterrows():
              if nome_prod in str(v_row["Descricao"]).lower():
                vendas_semana += 1

          cor_estoque = "red" if qtd <= min_q else "green"
          alerta_txt = " (Baixo!)" if qtd <= min_q else ""

          card_html = f"""
          <div style="font-size: 11px; line-height: 1.3; margin-bottom: 5px;">
            <b style="font-size: 12px; display: block; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{produto_nome}</b>
            <div>Custo: R$ {custo:.2f}</div>
            <div>Venda: R$ {venda:.2f}</div>
            <div>Margem: <b>{margem:.1f}%</b></div>
            <div>Estoque: <b style="color: {cor_estoque};">{qtd} un.{alerta_txt}</b></div>
            <div style="color: #0b7a20;">Vendas (7d): <b>{vendas_semana} un.</b></div>
          </div>
          """
          st.markdown(card_html, unsafe_allow_html=True)

          # Botão Alterar que abre o modal de edição e exclusão
          with st.popover("✏️ Alterar", use_container_width=True):
            st.markdown(f"### Editar: {produto_nome}")
            
            with st.form(key=f"form_alt_{row['ID']}"):
              novo_nome = st.text_input("Nome", value=produto_nome)
              
              lista_cats = ["Bebidas", "Porções", "Pratos Principais", "Sobremesas", "Insumos", "Outros"]
              cat_index = lista_cats.index(cat_atual) if cat_atual in lista_cats else 0
              nova_cat = st.selectbox("Categoria", lista_cats, index=cat_index)

              novo_custo = st.number_input("Preço Custo", value=float(custo), min_value=0.0, format="%.2f")
              novo_venda = st.number_input("Preço Venda", value=float(venda), min_value=0.0, format="%.2f")
              nova_qtd = st.number_input("Quantidade", value=int(qtd), min_value=0, step=1)
              novo_min = st.number_input("Estoque Mínimo", value=int(min_q), min_value=0, step=1)
              nova_img = st.file_uploader("Nova Foto (Opcional)", type=["png", "jpg", "jpeg"], key=f"img_up_{row['ID']}")

              salvar_alteracao = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)

              if salvar_alteracao:
                nova_margem = ((novo_venda - novo_custo) / novo_venda * 100) if novo_venda > 0 else 0.0
                caminho_final = caminho_img
                if nova_img:
                  caminho_final = redimensionar_e_salvar_imagem(nova_img, novo_nome)

                # Atualiza no DataFrame
                idx_linha = df_estoque[df_estoque["ID"] == row["ID"]].index
                df_estoque.loc[idx_linha, "Produto"] = novo_nome
                df_estoque.loc[idx_linha, "Categoria"] = nova_cat
                df_estoque.loc[idx_linha, "Preço de Custo (R$)"] = novo_custo
                df_estoque.loc[idx_linha, "Preço de Venda (R$)"] = novo_venda
                df_estoque.loc[idx_linha, "Margem (%)"] = round(nova_margem, 2)
                df_estoque.loc[idx_linha, "Quantidade"] = nova_qtd
                df_estoque.loc[idx_linha, "Estoque Mínimo"] = novo_min
                df_estoque.loc[idx_linha, "Imagem"] = caminho_final

                salvar_estoque(df_estoque)
                st.success("✅ Atualizado com sucesso!")
                st.rerun()

            # Opção de exclusão restrita apenas dentro do menu de alteração
            st.divider()
            if st.button("🗑️ Excluir Definitivamente", key=f"del_btn_{row['ID']}", use_container_width=True, type="primary"):
              df_estoque = df_estoque[df_estoque["ID"] != row["ID"]]
              salvar_estoque(df_estoque)
              st.success("Item excluído!")
              st.rerun()
