# Proposal

## Why

Primeira etapa do LLM no journal (`docs/handoff-llm.md` §4.1): cada artigo (reportagem, blog técnico, paper) ganha um parágrafo de aquecimento, um resumo curto para decidir se vale ler. É a mudança de menor risco para testar chave, custo, cache, tempo e falha antes da síntese das notícias.

## What Changes

- `Article.warmup`: texto puro opcional, escrito por IA.
- Porta `SummarizerPort.warmup(article) -> str | None` e o adaptador `DeepSeekSummarizer`, que chama `deepseek-flash` (raciocínio desligado) em `https://api.deepseek.com/chat/completions` só com `urllib`. Sem dependência nova: o pacote da Lambda continua só Python (§3.5).
- `BuildJournal.run()`: depois da seleção, aquece em paralelo os itens de `kind = "artigo"`, com prazo total. Erro, prazo ou orçamento estourados deixam o artigo sem aquecimento e o motivo vai para o relatório e o log; a edição sai do mesmo jeito.
- Orçamento por edição (US$ 5/mês, decidido em 2026-11-26): no máximo `max_calls` chamadas pagas (padrão 50), entrada cortada em `max_input_chars` (padrão 16.000) e saída em 600 tokens. Cache por `Article.key` em `llm-cache/warmup/<hash>.json` no storage do site: revisões do mesmo dia não pagam de novo.
- `journal.toml`: tabela opcional `[summarizer]`. Sem ela, ou sem `DEEPSEEK_API_KEY`, nada muda.
- Lambda: lê a chave do `SecureString` em `JOURNAL_DEEPSEEK_KEY_PARAMETER` (`/journal/deepseek-api-key`) e pode ler esse parâmetro.
- Site: em `artigos.html`, o aquecimento entra no lugar do resumo, marcado "Resumo por IA"; na página do artigo, acima do texto, com o selo "Resumo gerado por IA a partir de <fonte>". `articles.json` ganha `warmup`.

## Impact

- `domain/article.py`, `ports/`, `app/build.py`, novo `adapters/deepseek.py`, `adapters/static_site.py` e CSS, `config.py`, `cli.py`, `aws_lambda.py`, `adapters/storage.py`, `deploy/main.tf`, `journal.toml`, README, testes.
- Specs `article`, `journal-build`, `journal-config`, `static-site`, `aws-deploy`.
- Fora do escopo: notícias, agrupamento e síntese (§4.2 a §4.4).
