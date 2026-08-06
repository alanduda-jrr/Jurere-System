import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="PDV / Balcão - Jurerê", page_icon="🛍️", layout="wide")

if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
  st.warning("⚠️ Faça login na página inicial primeiro.")
  st.stop()

st.title("🛍️ PDV / Balcão - Gestão de Comandas")
st.markdown("Gerencie as comandas abertas e realize novas vendas no balcão.")

# Inicializa estado temporário para comandas nesta sessão se não existir
if "comandas" not in st.session_state:
  st.session_state["comandas"] = {
      "Alan": {"status": "Aberta", "itens": [("Água", 5.00), ("Refrigerante", 8.00)], "total": 579.00},
      "Cleyton": {"status": "Aberta", "itens": [("Cerveja", 12.00)], "total": 120.00},
      "Alex": {"status": "Aberta", "itens": [("Água", 5.00)], "total": 50.00},
      "Fran": {"status": "Fechada", "itens": [("Energetico", 18.00)], "total": 40.00},
      "Laura": {"status": "Fechada", "itens": [("Agua", 5.00)], "total": 39.00}
  }

# Botões de Ação Superior
col_b1, col_b2, col_space = st.columns([1, 1, 4])
with col_b1:
  if st.button("➕ Adicionar Comanda", use_container_width=True):
    st.session_state["modal_nova_comanda"] = True
with col_b2:
  if st.button("🛒 Balcão Direto", use_container_width=True):
    st.session_state["modal_balcao"] = True

# Modal / Formulário para Adicionar Comanda
if st.session_state.get("modal_nova_comanda", False):
  with st.form("form_nova_comanda"):
    st.subheader("Abrir Nova Comanda")
    nome_cliente = st.text_input("Nome do Cliente / Comanda")
    submitted = st.form_submit_button("Criar Comanda")
    if submitted:
      if nome_cliente:
        st.session_state["comandas"][nome_cliente] = {"status": "Aberta", "itens": [], "total": 0.0}
        st.session_state["modal_nova_comanda"] = False
        st.success(f"Comanda para {nome_cliente} aberta com sucesso!")
        st.rerun()
      else:
        st.warning("Digite um nome para a comanda.")

st.divider()

# --- COMANDAS ABERTAS ---
total_aberto = sum(v["total"] for k, v in st.session_state["comandas"].items() if v["status"] == "Aberta")
st.markdown(f"### 🟡 COMANDAS ABERTAS\n*Total em aberto: R$ {total_aberto:.2f}*")

cols_abertas = st.columns(4)
idx = 0
for nome, dados in st.session_state["comandas"].items():
  if dados["status"] == "Aberta":
    with cols_abertas[idx % 4]:
      # Caixa estilizado em amarelo para comandas abertas
      st.markdown(
          f"""
          <div style="background-color: #f4d03f; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 10px; font-weight: bold; font-size: 18px;">
              {nome}<br>
              <span style="font-size: 14px; font-weight: normal;">R$ {dados['total']:.2f}</span>
          </div>
          """,
          unsafe_allow_html=True
      )
      if st.button(f"Gerenciar {nome}", key=f"aberta_{nome}", use_container_width=True):
        st.session_state["comanda_selecionada"] = nome
    idx += 1

st.divider()

# --- COMANDAS FECHADAS ---
total_fechado = sum(v["total"] for k, v in st.session_state["comandas"].items() if v["status"] == "Fechada")
st.markdown(f"### 🟢 COMANDAS FECHADAS\n*Total fechadas: R$ {total_fechado:.2f}*")

cols_fechadas = st.columns(4)
idx_f = 0
for nome, dados in st.session_state["comandas"].items():
  if dados["status"] == "Fechada":
    with cols_fechadas[idx_f % 4]:
      # Caixa estilizado em verde para comandas fechadas
      st.markdown(
          f"""
          <div style="background-color: #27ae60; padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 10px; font-weight: bold; font-size: 18px;">
              {nome}<br>
              <span style="font-size: 14px; font-weight: normal;">R$ {dados['total']:.2f}</span>
          </div>
          """,
          unsafe_allow_html=True
      )
      if st.button(f"Ver {nome}", key=f"fechada_{nome}", use_container_width=True):
        st.session_state["comanda_selecionada"] = nome
    idx_f += 1

# Se o usuário clicar em gerenciar alguma comanda específica
if "comanda_selecionada" in st.session_state:
  c_nome = st.session_state["comanda_selecionada"]
  if c_nome in st.session_state["comandas"]:
    st.divider()
    st.subheader(f"Gerenciando Comanda: {c_nome} ({st.session_state['comandas'][c_nome]['status']})")
    
    col_det1, col_det2 = st.columns(2)
    with col_det1:
      st.write("Itens consumidos:")
      for item, preco in st.session_state["comandas"][c_nome]["itens"]:
        st.text(f"- {item}: R$ {preco:.2f}")
      st.markdown(f"**Total da Comanda: R$ {st.session_state['comandas'][c_nome]['total']:.2f}**")
      
    with col_det2:
      if st.session_state["comandas"][c_nome]["status"] == "Aberta":
        if st.button("🔒 Fechar Comanda / Pagamento"):
          st.session_state["comandas"][c_nome]["status"] = "Fechada"
          st.success(f"Comanda de {c_nome} fechada com sucesso!")
          del st.session_state["comanda_selecionada"]
          st.rerun()
      
      if st.button("❌ Fechar Detalhes"):
        del st.session_state["comanda_selecionada"]
        st.rerun()
