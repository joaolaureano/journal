# Proposal

## Why

O dono do projeto decidiu, em 2026-11-26, que o journal não roda aos domingos.

## What Changes

- O agendamento padrão passa de todo dia para segunda a sábado, às 08:00 de São Paulo: `cron(0 8 ? * MON-SAT *)`.
- A edição de segunda cobre o domingo sem buraco: a janela de 2 dias (`max_age_days = 2`) vai de sábado às 08:00 até segunda às 08:00, e o que sábado já publicou fica de fora pelo histórico.
- Uma execução manual no domingo continua possível, com `aws lambda invoke`.

## Impact

- `deploy/variables.tf`, `deploy/README.md`, `README.md`, spec `aws-deploy`. Nenhum código Python muda.
