import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Caixa e Comandas", page_icon="💵", layout="wide")

# Proteção de acesso
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
  st.warning("⚠️ Você precisa fazer o login na página inicial (App) para acessar o sistema.")
  st.stop()

# Barra lateral de navegação
st.sidebar.title(f"Usuário: {st.session_state.get('usuario', 'Convidado')}")
st.sidebar.markdown(f"Perfil: *{st.session_state.get('perfil', '')}*")
st.sidebar.divider()
if st.sidebar.button("Sair (Logout)", use_container_width=True):
  st.session_state["autenticado"] = False
  st.session_state["usuario"] = ""
  st.session_state["perfil"] = ""
  st.rerun()

ARQUIVO_COMANDAS = "comandas.csv"
ARQUIVO_CAIXA = "caixa_vendas.csv"


# Funções de manipulação de dados
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


df_comandas = carregar_comandas()
df_caixa = carregar_caixa()

st.title("💵 Caixa - Controle de Comandas e Vendas")
st.markdown("Gerencie comandas abertas pelas mesas/PDV, realize recebimentos e acompanhe o fluxo de caixa.")

# Abas do Caixa
aba1, aba2, aba3 = st.tabs(
    ["📋 Comandas Abertas", "⚡ Vendas Diretas de Balcão", "📊 Relatório e Fechamento"]
)

with aba1:
  st.subheader("Gerenciamento de Comandas Abertas (Mesas / PDV)")

  comandas_abertas = df_comandas[df_comandas["Status"] == "Aberta"] if not df_comandas.empty else pd.DataFrame()

  if comandas_abertas.empty:
    st.info("Nenhuma comanda aberta no momento.")
  else:
    # Agrupa por cliente/mesa para facilitar a visualização
    clientes_comandas = comandas_abertas["Cliente_Mesa"].unique()
    cliente_selecionado = st.selectbox("Selecione a Comanda / Mesa / Cliente:", clientes_comandas)

    if cliente_selecionado:
      itens_comanda = comandas_abertas[comandas_abertas["Cliente_Mesa"] == cliente_selecionado]

      st.markdown(f"### Detalhes da Comanda: **{cliente_selecionado}**")
      st.dataframe(itens_comanda[["Produto", "Quantidade", "Valor_Total"]], use_container_width=True)

      total_a_pagar = itens_comanda["Valor_Total"].sum()
      st.markdown(f"#### **Total a Pagar: R$ {total_a_pagar:.2f}**")

      forma_pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix"], key=f"pgto_{cliente_selecionado}")

      if st.button("💵 Fechar e Pagar Comanda", type="primary", use_container_width=True):
        # Registra a venda no caixa geral
        novo_id_venda = int(df_caixa["ID_Venda"].max() + 1) if not df_caixa.empty and "ID_Venda" in df_caixa.columns else 1
        
        nova_venda_caixa = pd.DataFrame([{
            "ID_Venda": novo_id_venda,
            "Tipo": "Comanda / Mesa",
            "Descricao": f"Fechamento Comanda: {cliente_selecionado}",
            "Valor": total_a_pagar,
            "Forma_Pagamento": forma_pgto,
            "Horario": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S")
        }])

        df_caixa = pd.concat([df_caixa, nova_venda_caixa], ignore_index=True)
        salvar_caixa(df_caixa)

        # Atualiza o status da comanda para Fechada
        df_comandas.loc[df_comandas["Cliente_Mesa"] == cliente_selecionado, "Status"] = "Fechada"
        salvar_comandas(df_comandas)

        st.success(f"Comanda de '{cliente_selecionado}' paga e fechada com sucesso!")
        st.rerun()

with aba2:
  st.subheader("Registro de Venda Direta (Balcão)")
  st.markdown("Para vendas imediatas que não utilizam comandas de mesas.")

  with st.form("form_venda_balcao", clear_on_submit=True):
    desc_venda = st.text_input("Descrição dos Itens / Produto Vendido")
    valor_venda = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
    forma_pgto_balcao = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix"], key="pgto_balcao")

    submit_balcao = st.form_submit_button("Registrar e Concluir Venda", use_container_width=True)

    if submit_balcao:
      if not desc_venda or valor_venda <= 0:
        st.error("Preencha a descrição e um valor válido para a venda.")
      else:
        novo_id_venda = int(df_caixa["ID_Venda"].max() + 1) if not df_caixa.empty and "ID_Venda" in df_caixa.columns else 1
        
        nova_venda_caixa = pd.DataFrame([{
            "ID_Venda": novo_id_venda,
            "Tipo": "Balcão (Direto)",
            "Descricao": desc_venda,
            "Valor": valor_venda,
            "Forma_Pagamento": forma_pgto_balcao,
            "Horario": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S")
        }])

        df_caixa = pd.concat([df_caixa, nova_venda_caixa], ignore_index=True)
        salvar_caixa(df_caixa)
        st.success("Venda de balcão registrada com sucesso!")
        st.rerun()

with aba3:
  st.subheader("Relatório de Entradas e Fechamento de Caixa")

  if df_caixa.empty:
    st.info("Nenhuma movimentação registrada no caixa ainda.")
  else:
    total_faturado = df_caixa["Valor"].sum()
    st.metric(label="Faturamento Total Registrado", value=f"R$ {total_faturado:.2f}")

    st.divider()
    st.markdown("### Histórico de Transações")
    st.dataframe(df_caixa, use_container_width=True)
