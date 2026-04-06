# Backlog Inicial de Issues

Lista pronta para criar as primeiras issues no GitHub.

## 1) Login e perfis de acesso
**Titulo sugerido:** Implementar autenticacao com perfis caixa e gerente
**Descricao:**
- Criar tela de login
- Criar tabela de usuarios
- Definir perfis: `CAIXA` e `GERENTE`
- Restringir acoes sensiveis para perfil gerente
**Criterios de aceite:**
- Usuario nao autenticado nao acessa sistema
- Permissoes aplicadas por perfil

## 2) Cancelamento de pedido com estorno
**Titulo sugerido:** Permitir cancelamento de pedido com estorno de estoque e caixa
**Descricao:**
- Adicionar acao de cancelamento para pedidos
- Devolver itens ao estoque
- Registrar estorno no caixa quando pedido ja estiver fechado
**Criterios de aceite:**
- Estoque volta ao valor correto apos cancelamento
- Movimento de estorno aparece no caixa

## 3) Relatorio diario
**Titulo sugerido:** Gerar relatorio diario de vendas e caixa
**Descricao:**
- Criar tela/filtro por data
- Exibir total vendido, total de entradas, saidas e saldo
- Mostrar quantidade de pedidos no periodo
**Criterios de aceite:**
- Relatorio apresenta dados corretos para qualquer data valida

## 4) Comprovante de pedido
**Titulo sugerido:** Implementar impressao de comprovante simples
**Descricao:**
- Gerar comprovante em formato imprimivel para pedido fechado
- Incluir itens, quantidades, total e data/hora
**Criterios de aceite:**
- Comprovante abre em layout pronto para impressao

## 5) Dashboard de produtos
**Titulo sugerido:** Criar dashboard com produtos mais vendidos
**Descricao:**
- Mostrar ranking de produtos por quantidade vendida
- Exibir periodo selecionado
**Criterios de aceite:**
- Ranking respeita o intervalo de datas selecionado
