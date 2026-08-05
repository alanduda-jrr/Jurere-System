import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PDV - Vendas e Comandas", page_icon="🛒", layout="wide")

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
ARQUIVO_COMANDAS = "comandas.csv"
ARQUIVO_CAIXA = "caixa_vendas.csv"


def carregar_estoque():
  if os.path.exists(ARQUIVO_ESTOQUE):
    return pd.read_csv(ARQUIVO_ESTOQUE)
  else:
    return pd.DataFrame(columns=["ID", "Produto", "Categoria", "Preço (R$)", "Quantidade", "Imagem"])


def salvar_estoque(df):
  df.to_csv(ARQUIVO_ESTOQUE, index=False)


def carregar_comandas():
  if os.path.exists(ARQUIVO_COMANDAS):
    return pd.read_csv(ARQUIVO_COMANDAS)
  else:
    return pd.DataFrame(columns=["ID_Comanda", "Cliente_Mesa", "Produto", "Quantidade", "Valor_Total", "Status"])


def salvar_comandas(df):
  df.to_csv(ARQUIVO_COMANDAS, index=False)


def carregar_caixa():
  if os.path.exists(ARQUIVO_CAIXA):
    return pd.read_csv(ARQUIVO_CAIXA)
  else:
    return pd.DataFrame(columns=["ID_Venda", "Tipo", "Descricao", "Valor", "Forma_Pagamento", "Horario"])


def salvar_caixa(df):
  df.to_csv(ARQUIVO_CAIXA, index=False)


df_estoque = carregar_estoque()
df_comandas = carregar_comandas()
df_caixa = carregar_caixa()

st.title("🛒 PDV - Frente de Caixa e Comandas")
st.markdown("Realize vendas diretas no balcão ou lance itens em comandas abertas por mesa/cliente.")

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

  # Exibição dos produtos estilo catálogo
  cols = st.columns(3)
  for idx, row in df_filtrado.reset_index().iterrows():
    with cols[idx % 3]:
      st.markdown(f"### {row['Produto']}")
      st.markdown(f"**Categoria:** {row['Categoria']}")
      st.markdown(f"**Preço:** R$ {row['Preço (R$)']:.2f}")
      st.markdown(f"**Disponível:** {row['Quantidade']} un.")

      # Opções de ação para o produto
      modo_venda = st.radio(
          "Destino da Venda:",
          ["Venda Balcão (Direta)", "Lançar em Comanda (Mesa)"],
          key=f"modo_{row['ID']}"
      )

      if modo_venda == "Lançar em Comanda (Mesa)":
        cliente_mesa = st.text_input("Nome do Cliente ou Mesa", key=f"cli_{row['ID']}")
        qtd_lancada = st.number_input("Qtd", min_value=1, max_value=int(row["Quantidade"]) if row["Quantidade"] > 0 else 1, value=1, key=f"qtd_{row['ID']}")

        if st.button(f"Lançar na Comanda", key=f"btn_comanda_{row['ID']}"):
          if not cliente_mesa:
            st.error("Informe o nome do cliente ou número da mesa.")
          elif row["Quantidade"] < qtd_lancada:
            st.error("Quantidade indisponível em estoque!")
          else:
            # Baixa no estoque
            indice_original = df_estoque[df_estoque["ID"] == row["ID"]].index[0]
            df_estoque.at[indice_original, "Quantidade"] -= qtd_lancada
            salvar_estoque(df_estoque)

            # Adiciona na comanda aberta
            novo_id_comanda = int(df_comandas["ID_Comanda"].max() + 1) if not df_comandas.empty and "ID_Comanda" in df_comandas.columns else 1
            valor_total_item = row["Preço (R$)"] * qtd_lancada

            nova_comanda = pd.DataFrame([{
                "ID_Comanda": novo_id_comanda,
                "Cliente_Mesa": cliente_mesa,
                "Produto": row["Produto"],
                "Quantidade": qtd_lancada,
                "Valor_Total": valor_total_item,
                "Status": "Aberta"
            }])

            df_comandas = pd.concat([df_comandas, nova_comanda], ignore_index=True)
            salvar_comandas(df_comandas)

            st.success(f"Item lançado na comanda de '{cliente_mesa}' com sucesso!")
            st.rerun()

      else:
        # Venda direta de balcão imediata
        if st.button(f"Concluir Venda Balcão", key=f"btn_balcao_{row['ID']}"):
          if row["Quantidade"] > 0:
            indice_original = df_estoque[df_estoque["ID"] == row["ID"]].index[0]
            df_estoque.at[indice_original, "Quantidade"] -= 1
            salvar_estoque(df_estoque)

            # Registra no caixa imediatamente
            novo_id_venda = int(df_caixa["ID_Venda"].max() + 1) if not df_caixa.empty and "ID_Venda" in df_caixa.columns else 1
            nova_venda_caixa = pd.DataFrame([{
                "ID_Venda": novo_id_venda,
                "Tipo": "Balcão (Direto)",
                "Descricao": f"1x {row['Produto']}",
                "Valor": row["Preço (R$)"],
                "Forma_Pagamento": "Dinheiro/Pix (Balcão)",
                "Horario": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S")
            }])

            df_caixa = pd.concat([df_caixa, nova_venda_caixa], ignore_index=True)
            salvar_caixa(df_caixa)

            st.success(f"Venda de '{row['Produto']}' realizada e registrada no caixa!")
            st.rerun()
          else:
            st.error("Produto esgotado no estoque!")

      st.markdown("---")
