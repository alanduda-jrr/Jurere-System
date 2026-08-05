import streamlit as st
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="Controle de Estoque - Jurerê", layout="wide")

# Inicializar dados na sessão se não existirem
if 'estoque' not in st.session_state:
    st.session_state['estoque'] = pd.DataFrame(columns=['ID', 'Nome', 'Descrição', 'Custo', 'Quantidade', 'Imagem'])

# Simples controle de senha
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234": # Altere a senha aqui se quiser
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Senha de acesso:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Senha de acesso:", type="password", on_change=password_entered, key="password")
        st.error("Senha incorreta.")
        return False
    else:
        return True

if check_password():
    st.title("📦 Sistema de Controle de Estoque - Jurerê")

    menu = ["Cadastrar Item", "Estoque Atual / Editar", "Movimentação"]
    escolha = st.sidebar.selectbox("Menu", menu)

    # 1. CADASTRAR ITEM
    if escolha == "Cadastrar Item":
        st.header("Cadastrar Novo Item")
        
        nome = st.text_input("Nome do Item")
        descricao = st.text_area("Descrição")
        custo = st.number_input("Preço de Custo (R$)", min_value=0.0, format="%.2f")
        quantidade = st.number_input("Quantidade Inicial", min_value=0, step=1)
        
        st.subheader("Imagem do Item")
        st.info("💡 Dica: Você pode tirar um print da tela, clicar na área abaixo e apertar Ctrl+V para colar a imagem diretamente!")
        
        # Opção de upload tradicional ou colar/tirar foto
        imagem_arquivo = st.file_uploader("Enviar imagem do computador", type=["png", "jpg", "jpeg"])
        
        img_bytes = None
        if imagem_arquivo is not None:
            img_bytes = imagem_arquivo.read()
            st.image(img_bytes, width=200)

        if st.button("Salvar Item"):
            if nome:
                novo_id = len(st.session_state['estoque']) + 1
                novo_dado = pd.DataFrame([{
                    'ID': novo_id,
                    'Nome': nome,
                    'Descrição': descricao,
                    'Custo': custo,
                    'Quantidade': quantidade,
                    'Imagem': img_bytes
                }])
                st.session_state['estoque'] = pd.concat([st.session_state['estoque'], novo_dado], ignore_index=True)
                st.success(f"Item '{nome}' cadastrado com sucesso!")
            else:
                st.warning("O nome do item é obrigatório.")

    # 2. ESTOQUE ATUAL E TELA DE EDIÇÃO
    elif escolha == "Estoque Atual / Editar":
        st.header("Estoque Atual e Gerenciamento")
        
        df = st.session_state['estoque']
        
        if df.empty:
            st.info("Nenhum item cadastrado no estoque ainda.")
        else:
            # Exibir tabela resumida sem a coluna de imagem em bytes para ficar limpo
            st.dataframe(df[['ID', 'Nome', 'Descrição', 'Custo', 'Quantidade']], use_container_width=True)
            
            st.markdown("---")
            st.subheader("✏️ Editar um Item Existente")
            
            # Selecionar o item pelo Nome ou ID
            item_ids = df['ID'].tolist()
            item_escolhido_id = st.selectbox("Selecione o ID do item que deseja editar:", item_ids)
            
            # Buscar dados atuais do item
            item_atual = df.loc[df['ID'] == item_escolhido_id].iloc[0]
            
            with st.form("form_edicao"):
                novo_nome = st.text_input("Nome", value=item_atual['Nome'])
                nova_desc = st.text_area("Descrição", value=item_atual['Descrição'])
                novo_custo = st.number_input("Custo (R$)", value=float(item_atual['Custo']), format="%.2f")
                nova_qtd = st.number_input("Quantidade", value=int(item_atual['Quantidade']), step=1)
                
                st.write("Imagem atual do item:")
                if item_atual['Imagem'] is not None:
                    st.image(item_atual['Imagem'], width=150)
                else:
                    st.write("Sem imagem cadastrada.")
                
                alterar_img = st.file_uploader("Enviar nova imagem (opcional)", type=["png", "jpg", "jpeg"])
                
                atualizar_btn = st.form_submit_button("Salvar Alterações")
                
                if atualizar_btn:
                    # Atualizar os dados no DataFrame da sessão
                    idx = st.session_state['estoque'][st.session_state['estoque']['ID'] == item_escolhido_id].index[0]
                    st.session_state['estoque'].at[idx, 'Nome'] = novo_nome
                    st.session_state['estoque'].at[idx, 'Descrição'] = nova_desc
                    st.session_state['estoque'].at[idx, 'Custo'] = novo_custo
                    st.session_state['estoque'].at[idx, 'Quantidade'] = nova_qtd
                    
                    if alterar_img is not None:
                        st.session_state['estoque'].at[idx, 'Imagem'] = alterar_img.read()
                        
                    st.success("Item atualizado com sucesso! Recarregue a página se necessário.")
                    st.rerun()

    # 3. MOVIMENTAÇÃO
    elif escolha == "Movimentação":
        st.header("Movimentação de Estoque (Entrada/Saída)")
        df = st.session_state['estoque']
        
        if df.empty:
            st.info("Nenhum item cadastrado para movimentar.")
        else:
            item_nome = st.selectbox("Selecione o Item", df['Nome'].tolist())
            tipo_mov = st.radio("Tipo de Movimentação", ["Entrada (Adicionar)", "Saída (Baixa)"])
            qtd_mov = st.number_input("Quantidade", min_value=1, step=1)
            
            if st.button("Confirmar Movimentação"):
                idx = st.session_state['estoque'][st.session_state['estoque']['Nome'] == item_nome].index[0]
                qtd_atual = int(st.session_state['estoque'].at[idx, 'Quantidade'])
                
                if tipo_mov == "Entrada (Adicionar)":
                    nova_qtd = qtd_atual + qtd_mov
                    st.session_state['estoque'].at[idx, 'Quantidade'] = nova_qtd
                    st.success(f"Entrada realizada! Nova quantidade de {item_nome}: {nova_qtd}")
                else:
                    if qtd_atual >= qtd_mov:
                        nova_qtd = qtd_atual - qtd_mov
                        st.session_state['estoque'].at[idx, 'Quantidade'] = nova_qtd
                        st.success(f"Baixa realizada! Nova quantidade de {item_nome}: {nova_qtd}")
                    else:
                        st.error("Quantidade em estoque insuficiente para essa baixa!")
