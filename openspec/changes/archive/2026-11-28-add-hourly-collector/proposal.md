# Coletor de hora em hora

## Why

Um feed só guarda os últimos itens publicados. A Revista Fórum cobre ~1,5 h, a CNN Brasil e a Jovem Pan ~6 h, InfoMoney e Money Times 6–7 h. A edição roda uma vez por dia, às 08:00, e vê só o que está no feed naquela hora. Para "puxar tudo do dia" e depois juntar as histórias repetidas, que é o plano do dono para virar um jornal de verdade (handoff §4.5), o journal precisa guardar o que cada feed mostrou ao longo do dia.

## What Changes

- **Pool de itens:** quando `[pool]` existe no `journal.toml`, cada leitura de uma fonte junta os itens do feed com os que ela guardou nas últimas `hours` horas (padrão 48) e salva o resultado no mesmo storage do site, em `pool/`. A edição passa a ver tudo o que os feeds mostraram desde a anterior. Sem `[pool]`, nada muda.
- **`journal collect`:** comando novo que só lê as fontes e atualiza o pool. Não publica e não chama a DeepSeek.
- **Lambda:** o evento `{"action": "collect"}` roda a coleta. Qualquer outro evento continua rodando a edição.
- **Agendamento:** uma segunda agenda chama a coleta a cada hora, no minuto 30, todos os dias, para não cair junto com a edição das 08:00. As versões antigas dos arquivos do pool expiram em 1 dia.
- **Filtro por endereço:** qualquer fonte aceita `paths = ["/politica/"]`, que só mantém os itens cujo link comece por um desses caminhos. Com ele, um feed geral entra em mais de uma seção.
- **Fontes no `journal.toml`:** `[pool]` e cinco entradas filtradas por endereço: CNN Brasil política (`/politica/`), CNN Brasil economia (`/economia/`), CNN Brasil internacional (`/internacional/`), Jovem Pan política e Jovem Pan economia. As outras fontes de Política, Economia e Mundo já estão no ar.

Fora do escopo: agrupar histórias, classificar por tema e escrever os textos com LLM (próximos passos do handoff §5); Tecnologia; o paper clássico do dia.

## Capabilities

### New Capabilities

- `source-pool`: guarda os itens que cada fonte mostrou em leituras anteriores e os devolve junto com o feed, dentro de uma janela de horas; inclui a coleta sem publicação.

### Modified Capabilities

- `journal-config`: tabela opcional `[pool]` com `hours` e opção `paths` em qualquer fonte.
- `aws-deploy`: o handler aceita a ação `collect`; a infraestrutura agenda a coleta de hora em hora e expira as versões antigas do pool.

## Impact

- Código: adapter novo `adapters/pool.py`; `cli.py` (comando `collect` e o pool em `run`); `aws_lambda.py`; `config.py`; `app/sectioned.py` (filtro por endereço); `adapters/storage.py` (`pool` passa a marcar um diretório como site do journal).
- Infra: `deploy/main.tf` e `deploy/variables.tf` (agenda nova e regra de ciclo de vida).
- Custo na AWS: 24 execuções curtas da Lambda por dia, dentro da camada gratuita, e cerca de 20 mil PUTs e 20 mil GETs no S3 por mês com as ~28 fontes, menos de US$ 0,15 por mês.
- Os arquivos do pool ficam no bucket servido pelo CloudFront, como o `llm-cache/`. São texto de feed, que já é público.
- Nenhuma chamada à DeepSeek: a coleta não gera textos.
