import os
import pandas as pd
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Sistema Jurerê", page_icon="📊", layout="wide")

# Inicializa o estado de autenticação se não existir
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False

# Tela de Login simples caso não esteja autenticado
if not st.session_state["autenticado"]:
  st.title("🔐 Login do Sistema")
  with st.form("form_login"):
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    submit = st.form_submit_button("Entrar")
    if submit:
      # Login padrão para liberar o acesso
      if usuario and senha:
        st.session_state["autenticado"] = True
        st.session_state["usuario_nome"] = usuario
        st.rerun()
      else:
        st.warning("Preencha usuário e senha.")
  st.stop()

# Menu lateral e estrutura principal
st.sidebar.markdown(f"**Bem-vindo(a),**\n\n{st.session_state.get('usuario_nome', 'Administrador')}")
st.sidebar.divider()
st.sidebar.markdown("### 📂 Módulos do Sistema")
modulo_selecionado = st.sidebar.selectbox("Selecione o Módulo", ["Início / Dashboard", "Caixa e Relatório de Vendas"])

if st.sidebar.button("Sair (Logout)"):
  st.session_state["autenticado"] = False
  st.rerun()

ARQUIVO_CAIXA = "caixa.csv"
ARQUIVO_ESTOQUE = "estoque.csv"

def carregar_caixa():
  if os.path.exists(ARQUIVO_CAIXA):
    try:
      df = pd.read_csv(ARQUIVO_CAIXA)
      colunas_padrao = ["ID_Venda", "Tipo", "Descricao", "Valor", "Forma_Pagamento", "Horario"]
      for col in colunas_padrao:
        if col not in df.columns:
          df[col] = None
      return df
    except Exception:
      return pd.DataFrame(columns=["ID_Venda", "Tipo", "Descricao", "Valor", "Forma_Pagamento", "Horario"])
  return pd.DataFrame(columns=["ID_Venda", "Tipo", "Descricao", "Valor", "Forma_Pagamento", "Horario"])

def carregar_estoque():
  if os.path.exists(ARQUIVO_ESTOQUE):
    try:
      return pd.read_csv(ARQUIVO_ESTOQUE)
    except Exception:
      return pd.DataFrame()
  return pd.DataFrame()

# -------------------------------------------------------------
# MÓDULO: INÍCIO / DASHBOARD
# -------------------------------------------------------------
if modulo_selecionado == "Início / Dashboard":
  st.title("📊 Painel Inicial - Sistema Jurerê")
  st.markdown("Visão geral rápida do sistema comercial.")

  df_caixa = carregar_caixa()
  df_estoque = carregar_estoque()

  total_hoje = 0.0
  qtd_vendas_hoje = 0

  if not df_caixa.empty and "Horario" in df_caixa.columns:
    df_caixa["Horario"] = pd.to_datetime(df_caixa["Horario"], errors="coerce")
    df_caixa["Data"] = df_caixa["Horario"].dt.date
    df_caixa["Valor"] = pd.to_numeric(df_caixa["Valor"], errors="coerce").fillna(0.0)
    
    hoje = datetime.now().date()
    vendas_hoje = df_caixa[(df_caixa["Data"] == hoje) & (df_caixa["Tipo"] == "Venda")]
    total_hoje = vendas_hoje["Valor"].sum()
    qtd_vendas_hoje = len(vendas_hoje)

  total_produtos = len(df_estoque) if not df_estoque.empty else 0

  c1, c2, c3 = st.columns(3)
  with c1:
    st.metric("Status do Caixa", "Aberto", "Operando")
  with c2:
    st.metric("Produtos Cadastrados", f"{total_produtos} itens")
  with c3:
    st.metric("Vendas Hoje", f"R$ {total_hoje:.2f}", f"{qtd_vendas_hoje} realizadas")

# -------------------------------------------------------------
# MÓDULO: CAIXA E RELATÓRIO DE VENDAS
# -------------------------------------------------------------
elif modulo_selecionado == "Caixa e Relatório de Vendas":
  st.title("💵 Caixa e Relatório de Vendas")
  st.markdown("Gerenciamento de faturamento, vendas realizadas e fechamento de caixa.")

  df_caixa = carregar_caixa()

  if df_caixa.empty or df_caixa["Valor"].dropna().empty:
    st.info("📭 Nenhuma movimentação registrada no caixa ainda. Realize vendas pelo PDV para preencher os relatórios.")
  else:
    df_caixa["Horario"] = pd.to_datetime(df_caixa["Horario"], errors="coerce")
    df_caixa["Data"] = df_caixa["Horario"].dt.date
    df_caixa["Valor"] = pd.to_numeric(df_caixa["Valor"], errors="coerce").fillna(0.0)

    hoje = datetime.now().date()
    
    col_m1, col_m2, col_m3 = st.columns(3)
    
    vendas_hoje = df_caixa[(df_caixa["Data"] == hoje) & (df_caixa["Tipo"] == "Venda")]
    total_hoje = vendas_hoje["Valor"].sum()
    qtd_vendas_hoje = len(vendas_hoje)

    total_geral = df_caixa[df_caixa["Tipo"] == "Venda"]["Valor"].sum()

    with col_m1:
      st.metric("Faturamento Hoje", f"R$ {total_hoje:.2f}", f"{qtd_vendas_hoje} vendas realizadas")
    with col_m2:
      st.metric("Faturamento Acumulado Geral", f"R$ {total_geral:.2f}")
    with col_m3:
      st.metric("Status do Caixa", "Aberto", "Operando normalmente")

    st.divider()

    st.subheader("📊 Vendas por Forma de Pagamento (Hoje)")
    if not vendas_hoje.empty:
      resumo_pagamento = vendas_hoje.groupby("Forma_Pagamento")["Valor"].sum().reset_index()
      resumo_pagamento.columns = ["Forma de Pagamento", "Total Arrecadado (R$)"]
      st.dataframe(resumo_pagamento, use_container_width=True, hide_index=True)
    else:
      st.info("Nenhuma venda registrada hoje até o momento.")

    st.divider()

    st.subheader("📜 Histórico Completo de Movimentações")
    
    tipo_filtro = st.selectbox("Filtrar por Tipo:", ["Todos", "Venda", "Sangria/Retirada", "Suprimento"])
    if tipo_filtro != "Todos":
      df_exibicao = df_caixa[df_caixa["Tipo"] == tipo_filtro]
    else:
      df_exibicao = df_caixa

    st.dataframe(
        df_exibicao.sort_values(by="Horario", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID_Venda": "ID",
            "Tipo": "Tipo",
            "Descricao": "Descrição",
            "Valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
            "Forma_Pagamento": "Forma de Pagamento",
            "Horario": "Data/Hora",
            "Data": None
        }
    )
