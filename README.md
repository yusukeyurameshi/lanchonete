# Sistema de Lanchonete (MVP)

Projeto inicial para controle de:
- Caixa
- Estoque
- Pedidos

## Tecnologias
- Python 3.11+
- Flask
- SQLite

## Como executar
1. Criar ambiente virtual:
   - PowerShell:
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
2. Instalar dependencias:
   - `pip install -r requirements.txt`
3. Iniciar o sistema:
   - `python app.py`
4. Abrir no navegador:
   - `http://127.0.0.1:5000`

## Funcionalidades do MVP
- Cadastro de produtos com preco e estoque inicial
- Criacao de pedido (baixa estoque automaticamente)
- Fechamento de pedido (lanca entrada no caixa)
- Lancamento manual de entrada/saida no caixa
- Endpoints simples para integracao:
  - `GET /api/products`
  - `GET /api/orders`
  - `GET /api/cash/summary`

## Proximos passos sugeridos
- Autenticacao de usuarios (caixa/gerencia)
- Cancelamento de pedidos com estorno de estoque e caixa
- Relatorio diario por periodo
- Impressao de comprovante
