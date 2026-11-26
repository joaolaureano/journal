# Design

## Modelo e preço

`deepseek-flash` (DeepSeek-V4.1-Flash, o mesmo que o alias `deepseek-v4-flash`), sem raciocínio (`"thinking": {"type": "disabled"}`). Preço oficial consultado em 2026-11-26: US$ 0,15/M de entrada e US$ 0,60/M de saída fora do pico. O pico é 01-04 e 06-10 UTC em dias úteis, com o dobro do preço, e a edição roda às 11:00 UTC. Uso típico: ~50 artigos × ~3 mil tokens de entrada + ~200 de saída ≈ US$ 0,03 por edição.

Pior caso por edição: 50 chamadas × 16.000 caracteres (~5 mil tokens) + 600 tokens de saída ≈ US$ 0,11 no preço de pico. São ~US$ 3,30 por mês numa edição por dia, abaixo dos US$ 5.

## Cliente HTTP

O `urllib` da stdlib, como o `RssSource`. A API é um POST JSON simples, e o SDK da OpenAI traria `pydantic-core` e `jiter`, que são compilados e quebram o pacote da Lambda (§3.5). Timeout de 60 s por chamada e nenhuma nova tentativa: o artigo sai sem aquecimento e a próxima revisão tenta de novo.

## Onde fica cada regra

- **App** (`BuildJournal`): quais itens (`kind = "artigo"`), paralelismo (8 threads), prazo total (`warmup_timeout`, 180 s) e tolerância a falhas. Vale para qualquer `SummarizerPort`.
- **Adaptador** (`DeepSeekSummarizer`): cache, orçamento de chamadas pagas (um contador com lock, porque as threads compartilham o adaptador), corte da entrada, prompt e validação da saída.
- **Composição** (`cli.run`): monta o adaptador com a chave de `DEEPSEEK_API_KEY` e o storage do publicador. Assim o cache cai no mesmo lugar do site, local ou S3, e a Lambda não precisa de fiação extra.

## Injeção de prompt

O texto do artigo vai na mensagem do usuário, entre `<artigo>` e `</artigo>`, e o prompt de sistema diz que é dado e não instrução. A resposta é tratada como texto puro: espaços normalizados, vazia ou com `finish_reason` diferente de `stop` vira erro, e acima de 1.200 caracteres também. Na página, passa sempre por `escape()`.

## Cache

`llm-cache/warmup/<sha256(key)[:16]>.json` com `{"key", "model", "warmup"}`. O cache é lido antes do orçamento: um acerto não conta como chamada. O `LocalStorage` passa a aceitar um diretório com `llm-cache/` como site do journal, porque o cache pode ser gravado antes da primeira publicação.
