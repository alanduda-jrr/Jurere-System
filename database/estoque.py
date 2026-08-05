# código completo aquiimport os
import pandas as pd

ARQUIVO_ESTOQUE = "estoque.csv"


def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        try:
            df = pd.read_csv(ARQUIVO_ESTOQUE)

            colunas_necessarias = [
                'ID',
                'Nome',
                'Categoria',
                'Descrição',
                'Preço_Custo',
                'Custo',
                'Quantidade',
                'Qtd_Minima',
                'Caminho_Imagem'
            ]

            for coluna in colunas_necessarias:
                if coluna not in df.columns:
                    df[coluna] = None

            return df

        except Exception:
            pass

    return pd.DataFrame(columns=[
        'ID',
        'Nome',
        'Categoria',
        'Descrição',
        'Preço_Custo',
        'Custo',
        'Quantidade',
        'Qtd_Minima',
        'Caminho_Imagem'
    ])


def salvar_dados(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)
