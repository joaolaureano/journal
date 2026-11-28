# Handoff: o que falta no journal (2026-11-28)

Leia este arquivo primeiro. O histórico das decisões sobre LLM e fontes está em
`docs/handoff-llm.md`; aqui fica só o estado atual e o caminho até o fim.

## 1. Objetivo do dono

"Não me sinto lendo um jornal de verdade." O journal deve ler como um jornal: poucas fontes lidas
por inteiro, as notícias repetidas juntadas em histórias escritas numa voz única, e uma capa
diagramada como a de um jornal. O backend dessa visão está pronto. Faltam ligar as histórias em
produção e desenhar a capa.

## 2. O que está no ar

Site: <https://d2e7f4g64n2qyp.cloudfront.net>. Edição de segunda a sábado às 08:00 de São Paulo.

| Seção | Fontes |
|---|---|
| Política | g1 política, JOTA, Revista Fórum, CNN Brasil política (`/politica/`), Jovem Pan política (`/politica/`) |
| Economia | g1 economia, InfoMoney, Money Times, Seu Dinheiro, CNN Brasil economia, Jovem Pan economia |
| Mundo | g1 mundo, Opera Mundi, CNN Brasil internacional (`/internacional/`) |
| Blogs técnicos | Martin Fowler, Pragmatic Engineer, Cloudflare, Daniel Lemire, Marc Brooker, Murat Demirbas, Trail of Bits, Krebs on Security, Import AI, Fabio Akita, Minuto da Segurança, Schneier on Security (os três desde 28/11, a pedido do dono) |
| Matemática | Terence Tao, The Aperiodical |
| Papers | The Morning Paper: um paper clássico por dia, do arquivo (`rss-archive`) |
| Rio Grande do Sul | O Sul, Litoral na Rede, Rádio Guaíba |

**As fontes estão consolidadas.** Não reabra a lista: O Antagonista, o arXiv filtrado, Ciência e
Tecnologia ficaram de fora por decisão do dono.

Peças em funcionamento:

- **Pool e coletor de hora em hora:** `[pool]` guarda o que cada feed mostrou nas últimas 48 h em
  `pool/`. A agenda `journal-collect` (minuto 30 de cada hora) chama a Lambda com
  `{"action": "collect"}`.
- **Filtro por endereço** (`paths`): um feed geral entra em mais de uma seção.
- **Aquecimento por IA** (`[summarizer]`, DeepSeek) nos itens `kind = "artigo"`.
- **Histórias** (`[stories]`): agrupamento, ranking, texto em voz única com fontes por parágrafo,
  divergências e página própria. **Ligadas desde 28/11**, depois de cinco rodadas reais locais
  (mudança `tighten-stories`). Limite conhecido: o agrupador ainda junta, às vezes, 1 a 3 itens
  de outro fato numa história; o texto quase sempre os ignora, mas eles aparecem entre as fontes.
  O modo de raciocínio no agrupador foi testado e descartado (~3 min e resposta cortada).
- **Capa diagramada** (`redesign-front-page`): manchete com foto, quatro chamadas, notas, faixas
  por seção em cards, aba Artigos em cards horizontais; tema claro, fonte do sistema.

## 3. O que falta, em ordem

**Estado em 28/11 (fim do dia):** 3.1, 3.2 e 3.3 estão feitos, e a primeira edição com histórias
saiu no sábado, 28/11, às 08:02. Depois dela entraram: histórias que cobrem todas as fontes numa
ordem fluida (`fuller-stories`), o filtro de grupos por palavras em comum (`check-story-groups`),
a hora de publicação de cada fonte e a regra dos números voláteis (`volatile-numbers`), o menu de
edições compartilhado, o favicon e três fontes (Fabio Akita, Minuto da Segurança, Schneier).
Na edição de segunda, 30/11, confira no log `N stories, N written` (o prazo da escrita agora é
240 s) e, nas histórias, se números de horas diferentes deixaram de virar divergência.
O que segue é o registro de como cada passo foi feito.

### 3.1 Arquivar o coletor (pequeno)

A mudança `add-hourly-collector` está completa, mas ainda não arquivada: falta ver uma coleta
rodar na AWS. Confira no log:

```sh
aws logs filter-log-events --profile agent --log-group-name /aws/lambda/journal-build \
  --filter-pattern collected --query 'events[].message' --output text
```

Se aparecer `collected N articles from M of 28 sources`, rode
`openspec archive add-hourly-collector -y`, escreva o `## Purpose` do spec novo `source-pool`
(o archive deixa um "TBD"), rode `openspec validate --specs --strict` e faça o commit.

### 3.2 Ligar as histórias em produção (precisa do OK do dono)

1. **Diga o custo antes e espere o OK:** ~US$ 0,03 por edição (1 chamada de agrupamento com
   ~35 mil tokens de entrada e 10 de escrita com ~6 mil cada, fora do pico), ~US$ 0,80 por mês.
   Confira os preços em <https://api-docs.deepseek.com/quick_start/pricing>, não de memória.
2. Com o OK, faça **uma** rodada local real para o dono ver a qualidade antes do deploy:
   uma cópia do `journal.toml` com `[stories]` e o storage local, e depois
   `uv run journal build --config <cópia>`, com a `DEEPSEEK_API_KEY` do shell do dono. Nunca
   mostre nem imprima a chave. Mostre a capa e duas ou três páginas de história, e procure:
   - agrupamentos errados (fatos diferentes juntados);
   - parágrafos com fonte que não diz aquilo;
   - divergências inventadas.
3. Ajuste os prompts (`GROUP_PROMPT` e `WRITE_PROMPT` em `src/journal/adapters/deepseek.py`) se
   preciso, com testes de API falsa.
4. Adicione `[stories]` ao `journal.toml`, faça o push (o CI publica o código) e confira o log da
   edição seguinte (`stories failed: ...` ou o resumo `N stories, N written`).

### 3.3 Diagramação da capa (o design, a última parte)

É a parte que o dono deixou por último. Comece **perguntando o jornal de referência** (ele ainda
não escolheu) e mostre um esboço antes de codar. O que já foi pedido (`docs/handoff-llm.md`
§4.5):

- capa com **manchete** e imagem grande, **chamadas médias** e **notas sem imagem**;
- as seções em **faixas**, rolando a página para baixo;
- só as imagens que os feeds mandam, com crédito, e uma diagramação que funcione sem foto;
- as histórias como o conteúdo principal; a lista "Todas as notícias" continua acessível;
- páginas de história e de item no mesmo estilo; celular e desktop;
- todo texto do modelo sempre escapado e sempre marcado como IA.

Para ver a capa com histórias sem gastar nada, use a prévia com agrupador e escritor
provisórios:

```sh
mkdir -p /tmp/preview
sed 's|out = "dist"|out = "site"|' journal.toml > /tmp/preview/journal.toml
env -u DEEPSEEK_API_KEY uv run python scripts/preview_stories.py /tmp/preview/journal.toml
open /tmp/preview/site/index.html
```

Os textos dessa prévia são os resumos das próprias fontes, com o título marcado `[prévia]`. Servem
para o layout, não para julgar a qualidade. O site é gerado em
`src/journal/adapters/static_site.py`, com os templates e o `style.css` em
`src/journal/adapters/templates/`. A especificação está em `openspec/specs/static-site/spec.md`.

## 4. Regras que valem sempre

- **Sem DeepSeek durante o desenvolvimento.** Builds locais rodam com `env -u DEEPSEEK_API_KEY`, e
  os testes usam fakes. Uma chamada real só com pedido do dono e o custo dito antes.
- **Fontes:**
  - texto completo no feed;
  - nenhum paywall, nem o medido;
  - nenhuma restrição a IA no `robots.txt`;
  - só RSS: nada de scraping, PDFs ou páginas baixadas.
- **Sem conferência frase a frase** ("Não teremos fact check por ora").
- **A chave da DeepSeek** fica só no SSM (`/journal/deepseek-api-key`). Ela nunca vai para o repo
  (que é público), o `journal.toml`, o Terraform ou a conversa.
- **OpenSpec em tudo:**
  - `openspec new change <nome>`, depois proposta, specs delta, design e tarefas;
  - implementar e marcar as tarefas;
  - `openspec archive <nome> -y`;
  - preencher o `## Purpose` de cada spec novo;
  - `openspec validate --specs --strict`. Requisitos com mais de 500 caracteres falham.
- **Antes de cada commit:** `uv run ruff check .`, `uv run ruff format --check .` e
  `uv run pytest -q`, com ~376 testes.
- **Commits:** em inglês, terminando com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Deploy:** o push na `main` publica o código da Lambda pelo CI. Mudanças em `deploy/` pedem
  `tofu apply` e o OK do dono. O dono roda o comando com o perfil `agent`:
  ```sh
  cd deploy && eval "$(aws configure export-credentials --profile agent --format env)" && unset AWS_PROFILE && tofu apply
  ```

## 5. Mapa rápido do código

| Onde | O quê |
|---|---|
| `src/journal/domain/` | `Article` (com `evergreen`), `Edition` (com `stories`), `Story`, `StoryText` |
| `src/journal/ports/` | fontes, publicador, histórico, `SummarizerPort`, `GrouperPort`, `WriterPort` |
| `src/journal/app/build.py` | a edição: janela, filtro, histórico, histórias, limite por seção, aquecimento |
| `src/journal/adapters/` | `rss.py`, `archive.py`, `pool.py`, `deepseek.py` (summarizer, grouper, writer), `static_site.py`, `s3.py` |
| `src/journal/cli.py` | `journal build` e `journal collect`, e onde as peças são montadas |
| `src/journal/aws_lambda.py` | o handler: edição, ou coleta com `{"action": "collect"}` |
| `scripts/preview_stories.py` | prévia local com histórias, sem LLM |
| `deploy/` | OpenTofu: bucket, CloudFront, Lambda, agendas `daily` e `collect` |
