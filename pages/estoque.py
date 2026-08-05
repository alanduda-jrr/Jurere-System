import os
import pandas as pd

ARQUIVO_ESTOQUE = "estoque.csv"


def dar_baixa_estoque(nome_produto, quantidade_vendida):
  if os.path.exists(ARQUIVO_ESTOQUE):
    df = pd.read_csv(ARQUIVO_ESTOQUE)

    # Localiza o produto pelo nome (ignorando maiúsculas/minúsculas)
    match = df[df["Produto"].str.lower() == nome_produto.lower()]

    if not match.empty:
      idx = match.index[0]
      estoque_atual = int(df.loc[idx, "Quantidade"])

      # Subtrai a quantidade (evita que fique abaixo de zero se preferir)
      nova_quantidade = max(0, estoque_atual - int(quantidade_vendida))
      df.loc[idx, "Quantidade"] = nova_quantidade

      # Salva de volta no mesmo arquivo do estoque
      df.to_csv(ARQUIVO_ESTOQUE, index=False)
      return True
  return False
