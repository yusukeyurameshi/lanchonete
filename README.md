# Lanchonete

Sistema simples para controle de caixa, estoque e pedidos de uma lanchonete pequena.

## Objetivo
Entregar um software leve e facil de usar no dia a dia do atendimento.

## Funcionalidades atuais (MVP)
- Cadastro de produtos com preco e estoque inicial
- Criacao de pedido com baixa automatica de estoque
- Fechamento de pedido com lancamento de entrada no caixa
- Lancamento manual de entrada/saida no caixa
- Resumo de caixa (entradas, saidas e saldo)
- API basica para integracoes

## Tecnologias
- Python 3.11+
- Flask
- SQLite
- HTML + CSS

## Executar localmente
1. Criar e ativar ambiente virtual (PowerShell):
`python -m venv .venv`
`.venv\Scripts\Activate.ps1`
2. Instalar dependencias:
`pip install -r requirements.txt`
3. Iniciar aplicacao:
`python app.py`
4. Abrir no navegador:
`http://127.0.0.1:5000`

## Endpoints da API
- `GET /api/products`
- `GET /api/orders`
- `GET /api/cash/summary`

## Estrutura do projeto
- `app.py`: aplicacao Flask e regras de negocio
- `schema.sql`: estrutura do banco SQLite
- `templates/index.html`: interface principal
- `static/style.css`: estilos da tela

## Roadmap
- [ ] Login com perfil de acesso (caixa e gerente)
- [ ] Cancelamento de pedidos com estorno de estoque e caixa
- [ ] Relatorio diario por periodo
- [ ] Impressao de comprovante
- [ ] Dashboard com produtos mais vendidos

## Backlog inicial de issues
As primeiras issues sugeridas estao em:
- `docs/ISSUES_BACKLOG.md`

## Licenca
Este projeto esta licenciado sob a UPL 1.0 (Universal Permissive License).
Veja o arquivo `LICENSE`.
