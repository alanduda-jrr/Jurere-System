# 0. INÍCIO
    if st.session_state['menu_selecionado'] == "Início":
        st.header("🏠 Início")
        st.markdown("Selecione abaixo para onde deseja navegar:")
        
        st.markdown("""
        <style>
        .card-container {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.04);
            height: 190px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="card-container">
                <div style="font-size: 32px; margin-bottom: 8px;">🛒</div>
                <h3 style="margin: 0 0 6px 0; color: #1f1f1f; font-size: 18px;">PDV (Vendas)</h3>
                <p style="color: #666; font-size: 13px; margin: 0; line-height: 1.4;">Realizar vendas e visualizar produtos por categoria.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar PDV", key="nav_pdv", use_container_width=True):
                st.session_state['menu_selecionado'] = "PDV (Vendas / Navegação)"
                st.session_state['menu_selectbox_widget'] = "PDV (Vendas / Navegação)"
                st.rerun()

        with col2:
            st.markdown("""
            <div class="card-container">
                <div style="font-size: 32px; margin-bottom: 8px;">📦</div>
                <h3 style="margin: 0 0 6px 0; color: #1f1f1f; font-size: 18px;">Estoque (Gerenciar)</h3>
                <p style="color: #666; font-size: 13px; margin: 0; line-height: 1.4;">Consultar tabela, cadastrar itens e editar preços ou quantidades.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Estoque", key="nav_estoque", use_container_width=True):
                st.session_state['menu_selecionado'] = "Estoque Atual / Editar"
                st.session_state['menu_selectbox_widget'] = "Estoque Atual / Editar"
                st.rerun()

        with col3:
            st.markdown("""
            <div class="card-container">
                <div style="font-size: 32px; margin-bottom: 8px;">💵</div>
                <h3 style="margin: 0 0 6px 0; color: #1f1f1f; font-size: 18px;">Caixa (Balcão)</h3>
                <p style="color: #666; font-size: 13px; margin: 0; line-height: 1.4;">Entradas e baixas manuais rápidas no estoque e balcão.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Acessar Caixa", key="nav_caixa", use_container_width=True):
                st.session_state['menu_selecionado'] = "Movimentação"
                st.session_state['menu_selectbox_widget'] = "Movimentação"
                st.rerun()
