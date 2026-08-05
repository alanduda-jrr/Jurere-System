import streamlit as st
import pandas as pd
from PIL import Image
import io
import os

st.set_page_config(page_title="Controle de Estoque e PDV - Jurerê", layout="wide")

ARQUIVO_ESTOQUE = "estoque.csv"

# Categorias padronizadas em ordem alfabética estrita
CATEGORIAS_PADRAO = [
    "Água",
    "Cervejas",
    "Drinks com álcool",
    "Isotônicos e energéticos",
    "Porções",
    "Refrigerantes",
    "Salgados fritos e assados",
    "Sobremesas",
    "Outros"
]

def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        try:
            df = pd.read_csv(ARQUIVO_ESTOQUE)
            colunas_necessarias = ['ID', 'Nome', 'Categoria', 'Descrição', 'Preço_Custo', 'Custo', 'Quantidade', 'Qtd_Minima', 'Caminho_Imagem']
            for col in colunas_necessarias:
                if col not in df.columns:
                    df[col] = None
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=['ID', 'Nome', 'Categoria', 'Descrição', 'Preço_Custo', 'Custo', 'Quantidade', 'Qtd_Minima', 'Caminho_Imagem'])

def salvar_dados(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

def processar_e_salvar_imagem(imagem_upload, nome_arquivo_destino):
    os.makedirs("imagens_produtos", exist_ok=True)
    caminho_completo = os.path.join("imagens_produtos", nome_arquivo_destino)
    
    try:
        img = Image.open(imagem_upload)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        img.save(caminho_completo, "JPEG", quality=90)
        return caminho_completo
    except Exception as e:
        st.error(f"Erro ao processar imagem: {e}")
        return None

if 'estoque' not in st.session_state:
    st.session_state['estoque'] = carregar_dados()

if 'menu_selecionado' not in st.session_state:
    st.session_state['menu_selecionado'] = "Início"

def check_password():
    def password_entered():
        if st.session_state["password"] == "1234":
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
    st.title("🍔 Sistema PDV & Controle de Estoque - Jurerê")

    menu = ["Início", "PDV (Vendas / Navegação)", "Cadastrar Item", "Estoque Atual / Editar", "Movimentação"]
    
    if 'menu_selecionado' not in st.session_state or st.session_state['menu_selecionado'] not in menu:
        st.session_state['menu_selecionado'] = menu[0]

    escolha = st.sidebar.selectbox("Menu", menu, index=menu.index(st.session_state['menu_selecionado']), key="menu_selectbox_widget")
    if escolha != st.session_state['menu_selecionado']:
        st.session_state['menu_selecionado'] = escolha

    # 0. INÍCIO (TELA DE NAVEGAÇÃO EM GALERIA/ÍCONES)
    if st.session_state['menu_selecionado'] == "Início":
        st.header("🏠 Início")
        st.markdown("Selecione abaixo para onde deseja navegar:")
        
        st.markdown("""
        <style>
        div.stButton > button {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: 0.3s;
            width: 100%;
            color: #31333F;
        }
        div.stButton > button:hover {
            box-shadow: 0 6px 12px rgba(0,0,0,0.12);
            border-color: #2b6cb0;
            background-color: #fafafa;
            color: #2b6cb0;
        }
        </style>
        """, unsafe_allow_html=True)

        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            if st.button("🛒\n\n### PDV / Vendas\nRealizar vendas, visualizar produtos por categoria em formato de galeria.", key="btn_dash_pdv", use_container_width=True):
                st.session_state['menu_selecionado'] = "PDV (Vendas / Navegação)"
                st.rerun()

            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

            if st.button("📦\n\n### Estoque Atual / Editar\nConsultar tabela de estoque, conferir itens e editar preços ou quantidades.", key="btn_dash_estoque", use_container_width=True):
                st.session_state['menu_selecionado'] = "Estoque Atual / Editar"
                st.rerun()

        with col_d2:
            if st.button("✨\n\n### Cadastrar Novo Item\nAdicionar novos produtos com foto, nome, categorias e preços obrigatórios.", key="btn_dash_cadastrar", use_container_width=True):
                st.session_state['menu_selecionado'] = "Cadastrar Item"
                st.rerun()

            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

            if st.button("🔄\n\n### Movimentação\nEntradas e baixas manuais rápidas no estoque.", key="btn_dash_mov", use_container_width=True):
                st.session_state['menu_selecionado'] = "Movimentação"
                st.rerun()

    # 1. PDV (PONTO DE VENDA - GALERIA PADRONIZADA)
    elif st.session_state['menu_selecionado'] == "PDV (Vendas / Navegação)":
        st.header("🛒 PDV - Frente de Caixa (Galeria)")
        df = st.session_state['estoque']
        
        if df.empty:
            st.info("Nenhum item cadastrado no estoque ainda. Cadastre itens no menu lateral ou início.")
        else:
            categorias_disponiveis = sorted(df['Categoria'].dropna().unique().tolist())
            if not categorias_disponiveis:
                categorias_disponiveis = ["Geral"]
                
            categoria_selecionada = st.selectbox("📂 Selecione a Categoria:", categorias_disponiveis)
            
            itens_categoria = df[df['Categoria'] == categoria_selecionada]
            
            st.markdown("---")
            st.subheader(f"Itens da Categoria: {categoria_selecionada}")
            
            st.markdown("""
            <style>
            .product-card {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                text-align: center;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .product-img-container {
                width: 100%;
                height: 160px;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                background-color: #f9f9f9;
                border-radius: 6px;
                margin-bottom: 10px;
            }
            .product-img-container img {
                max-height: 100%;
                max-width: 100%;
                object-fit: contain;
            }
            </style>
            """, unsafe_allow_html=True)

            cols = st.columns(3)
            for index, row in itens_categoria.reset_index().iterrows():
                with cols[index % 3]:
                    img_path = row['Caminho_Imagem']
                    img_html = ""
                    if pd.notna(img_path) and os.path.exists(str(img_path)):
                        import base64
                        with open(str(img_path), "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode()
                        img_html = f'<div class="product-img-container"><img src="data:image/jpeg;base64,{encoded_string}"></div>'
                    else:
                        img_html = '<div class="product-img-container"><span style="color: #aaa; font-size: 13px;">Sem imagem</span></div>'

                    preco_venda_val = row['Custo'] if pd.notna(row['Custo']) else row.get('Preço_Custo', 0)
                    qtd_val = int(row['Quantidade']) if pd.notna(row['Quantidade']) else 0
                    desc_val = row['Descrição'] if pd.notna(row['Descrição']) and str(row['Descrição']).strip() != "" else ""

                    st.markdown(f"""
                    <div class="product-card">
                        <div>
                            <h4 style="margin: 0 0 10px 0; color: #333; font-size: 18px;">{row['Nome']}</h4>
                            {img_html}
                            <p style="margin: 5px 0; font-size: 15px;"><strong>Preço:</strong> R$ {float(preco_venda_val):.2f}</p>
                            <p style="margin: 5px 0; font-size: 14px; color: #555;"><strong>Estoque:</strong> {qtd_val} un.</p>
                            <p style="margin: 5px 0; font-size: 13px; color: #777; font-style: italic;">{desc_val}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Registrar Venda", key=f"venda_{row['ID']}", use_container_width=True):
                        if qtd_val > 0:
                            idx = st.session_state['estoque'][st.session_state['estoque']['ID'] == row['ID']].index[0]
                            st.session_state['estoque'].at[idx, 'Quantidade'] = qtd_val - 1
                            salvar_dados(st.session_state['estoque'])
                            st.success(f"Venda de '{row['Nome']}' realizada!")
                            st.rerun()
                        else:
                            st.error("Produto esgotado!")
                    st.markdown("<br>", unsafe_allow_html=True)

    # 2. CADASTRAR ITEM
    elif st.session_state['menu_selecionado'] == "Cadastrar Item":
        st.header("✨ Cadastrar Novo Item")
        st.markdown("Preencha os campos abaixo de forma rápida utilizando a tecla **Tab**.")

        with st.form("form_cadastro_item", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                nome = st.text_input("Nome do Item *", placeholder="Ex: Heineken 600ml")
                cat_escolhida = st.selectbox("Categoria (Obrigatório) *", CATEGORIAS_PADRAO, index=None, placeholder="Selecione uma categoria...")
                if cat_escolhida == "Outros":
                    categoria = st.text_input("Especifique a nova categoria *")
                else:
                    categoria = cat_escolhida
                
                preco_custo = st.number_input("Preço de Custo (R$) *", min_value=0.0, format="%.2f", value=0.0)

            with col2:
                preco_venda = st.number_input("Preço de Venda (R$) *", min_value=0.0, format="%.2f", value=0.0)
                quantidade_inicial = st.number_input("Quantidade Inicial", min_value=0, step=1, value=0)
                quantidade_minima = st.number_input("Quantidade Mínima (Alerta)", min_value=0, step=1, value=5)

            descricao = st.text_area("Descrição do Produto", placeholder="Detalhes, ingredientes ou observações...", height=100)

            if preco_venda > 0 and preco_custo > 0:
                lucro_rs = preco_venda - preco_custo
                margem_pct = (lucro_rs / preco_venda) * 100
                markup_pct = (lucro_rs / preco_custo) * 100
                st.info(f"📊 **Análise de Margem:** Lucro de **R$ {lucro_rs:.2f}** | Margem: **{margem_pct:.1f}%** (Markup: {markup_pct:.1f}%)")

            st.markdown("---")
            st.subheader("🖼️ Foto do Produto")
            imagem_arquivo = st.file_uploader("Escolher imagem", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

            submitted = st.form_submit_button("💾 Salvar Novo Item no Estoque", use_container_width=True)

            if submitted:
                categoria_valida = categoria is not None and str(categoria).strip() != ""
                if nome and categoria_valida and preco_custo > 0 and preco_venda > 0:
                    caminho_salvo = None
                    if imagem_arquivo is not None:
                        nome_limpo = "".join(c for c in nome if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
                        if not nome_limpo:
                            nome_limpo = "produto"
                        nome_arquivo_final = f"{nome_limpo}_{os.urandom(4).hex()}.jpg"
                        caminho_salvo = processar_e_salvar_imagem(imagem_arquivo, nome_arquivo_final)

                    df_atual = st.session_state['estoque']
                    novo_id = int(df_atual['ID'].max() + 1) if not df_atual.empty and pd.notna(df_atual['ID'].max()) else 1
                    
                    novo_dado = pd.DataFrame([{
                        'ID': novo_id,
                        'Nome': nome,
                        'Categoria': categoria,
                        'Descrição': descricao,
                        'Preço_Custo': preco_custo,
                        'Custo': preco_venda,
                        'Quantidade': quantidade_inicial,
                        'Qtd_Minima': quantidade_minima,
                        'Caminho_Imagem': caminho_salvo
                    }])
                    
                    st.session_state['estoque'] = pd.concat([df_atual, novo_dado], ignore_index=True)
                    salvar_dados(st.session_state['estoque'])
                    
                    st.session_state['menu_selecionado'] = "Início"
                    st.success(f"🎉 Item '{nome}' cadastrado com sucesso! Redirecionando para o Início...")
                    st.rerun()
                else:
                    st.warning("⚠️ Preencha todos os campos obrigatórios: **Nome**, **Categoria**, **Preço de Custo** e **Preço de Venda** (maiores que zero).")

    # 3. ESTOQUE ATUAL E TELA DE EDIÇÃO
    elif st.session_state['menu_selecionado'] == "Estoque Atual / Editar":
        st.header("Estoque Atual e Gerenciamento")
        df = st.session_state['estoque']
        
        if df.empty:
            st.info("Nenhum item cadastrado no estoque ainda.")
        else:
            cols_mostrar = [c for c in ['ID', 'Nome', 'Categoria', 'Preço_Custo', 'Custo', 'Quantidade', 'Qtd_Minima'] if c in df.columns]
            st.dataframe(df[cols_mostrar], use_container_width=True)
            
            st.markdown("---")
            st.subheader("✏️ Editar um Item Existente")
            
            item_ids = df['ID'].tolist()
            item_escolhido_id = st.selectbox("Selecione o ID do item que deseja editar:", item_ids)
            
            item_atual = df.loc[df['ID'] == item_escolhido_id].iloc[0]
            
            with st.form("form_edicao"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    novo_nome = st.text_input("Nome", value=item_atual['Nome'])
                    
                    cat_atual_val = item_atual['Categoria']
                    idx_cat = CATEGORIAS_PADRAO.index(cat_atual_val) if cat_atual_val in CATEGORIAS_PADRAO else len(CATEGORIAS_PADRAO)-1
                    nova_cat_escolhida = st.selectbox("Categoria", CATEGORIAS_PADRAO, index=idx_cat)
                    if nova_cat_escolhida == "Outros":
                        nova_categoria = st.text_input("Digite a categoria:", value=cat_atual_val)
                    else:
                        nova_categoria = nova_cat_escolhida
                        
                    pc_atual = float(item_atual['Preço_Custo']) if pd.notna(item_atual.get('Preço_Custo')) else 0.0
                    novo_preco_custo = st.number_input("Preço de Custo (R$)", value=pc_atual, format="%.2f")
                    
                    pv_atual = float(item_atual['Custo']) if pd.notna(item_atual.get('Custo')) else 0.0
                    novo_preco_venda = st.number_input("Preço de Venda (R$)", value=pv_atual, format="%.2f")

                with col_e2:
                    qtd_at = int(item_atual['Quantidade']) if pd.notna(item_atual.get('Quantidade')) else 0
                    nova_qtd = st.number_input("Quantidade", value=qtd_at, step=1)
                    
                    qtd_min_at = int(item_atual['Qtd_Minima']) if pd.notna(item_atual.get('Qtd_Minima')) else 5
                    nova_qtd_min = st.number_input("Quantidade Mínima", value=qtd_min_at, step=1)
                    
                    nova_desc = st.text_area("Descrição", value=item_atual['Descrição'] if pd.notna(item_atual['Descrição']) else "")
                
                st.write("Imagem atual do item:")
                img_path_atual = item_atual['Caminho_Imagem']
                if pd.notna(img_path_atual) and os.path.exists(str(img_path_atual)):
                    st.image(str(img_path_atual), width=150)
                else:
                    st.write("Sem imagem cadastrada.")
                
                alterar_img = st.file_uploader("Enviar nova imagem (opcional)", type=["png", "jpg", "jpeg", "webp"])
                
                atualizar_btn = st.form_submit_button("Salvar Alterações")
                
                if atualizar_btn:
                    idx = st.session_state['estoque'][st.session_state['estoque']['ID'] == item_escolhido_id].index[0]
                    st.session_state['estoque'].at[idx, 'Nome'] = novo_nome
                    st.session_state['estoque'].at[idx, 'Categoria'] = nova_categoria
                    st.session_state['estoque'].at[idx, 'Descrição'] = nova_desc
                    st.session_state['estoque'].at[idx, 'Preço_Custo'] = novo_preco_custo
                    st.session_state['estoque'].at[idx, 'Custo'] = novo_preco_venda
                    st.session_state['estoque'].at[idx, 'Quantidade'] = nova_qtd
                    st.session_state['estoque'].at[idx, 'Qtd_Minima'] = nova_qtd_min
                    
                    if alterar_img is not None:
                        nome_limpo = "".join(c for c in novo_nome if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
                        if not nome_limpo:
                            nome_limpo = "produto"
                        nome_arquivo_final = f"{nome_limpo}_{item_escolhido_id}.jpg"
                        
                        novo_caminho = processar_e_salvar_imagem(alterar_img, nome_arquivo_final)
                        if novo_caminho:
                            st.session_state['estoque'].at[idx, 'Caminho_Imagem'] = novo_caminho
                        
                    salvar_dados(st.session_state['estoque'])
                    st.success("Item atualizado com sucesso!")
                    st.rerun()

    # 4. MOVIMENTAÇÃO
    elif st.session_state['menu_selecionado'] == "Movimentação":
        st.header("Movimentação de Estoque Manual (Entrada/Saída)")
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
                    salvar_dados(st.session_state['estoque'])
                    st.success(f"Entrada realizada! Nova quantidade de {item_nome}: {nova_qtd}")
                else:
                    if qtd_atual >= qtd_mov:
                        nova_qtd = qtd_atual - qtd_mov
                        st.session_state['estoque'].at[idx, 'Quantidade'] = nova_qtd
                        salvar_dados(st.session_state['estoque'])
                        st.success(f"Baixa realizada! Nova quantidade de {item_nome}: {nova_qtd}")
                    else:
                        st.error("Quantidade em estoque insuficiente para essa baixa!")
