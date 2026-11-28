# Handoff: LLM no journal

Escrito em 2026-11-26, no fim da sessão que deixou o fluxo sem LLM pronto. É o ponto de partida
para a etapa que motivou o projeto: usar LLM para curar e escrever as notícias.

## 1. O objetivo, nas palavras do dono do projeto

- **Notícias:** em vez de várias notícias iguais espalhadas por fontes diferentes, o LLM junta o
  que trata do mesmo fato e escreve **um texto só**, numa voz única, "como se fosse um autor
  único". Se a fonte B complementa a A, o texto junta as duas. Se B **contradiz** A, esse é o caso
  mais valioso. Ainda está em aberto como mostrar isso (ver §6).
- **No máximo 10 notícias por edição, no total.** Cada uma é uma história sintetizada, não um
  item de feed. O limite atual de 10 por seção deixa de valer para as notícias.
- **Artigos** (reportagens, blogs técnicos, papers): o LLM escreve **um parágrafo de
  aquecimento**, um resumo curto para decidir se vale ler, e depois vem o artigo inteiro como hoje.
  **Nada mais muda nos artigos.**
- Não é deduplicação: nenhuma etapa deve descartar itens de outras fontes sobre o mesmo fato. Eles
  são a matéria-prima da síntese.

## 2. O que já existe (o fluxo sem LLM)

```
27 feeds RSS ──► RssSource (texto completo, fotos, datas pt-BR, arXiv limpo)
             ──► BuildJournal: dedup por URL, histórico (seen.json, 90 dias),
                 janela de 2 dias, filtro de palavras, limite por seção e tipo
             ──► Edition ──► StaticSitePublisher ──► S3 ──► CloudFront
```

- **Roda sozinho:** EventBridge Scheduler `journal-daily` chama a Lambda `journal-build` todo dia
  às 08:00 de São Paulo. Python 3.12, arm64, 256 MB, timeout de 600 s.
- **CI:** em todo push na `main`, o GitHub Actions roda ruff e pytest (244 testes), empacota com
  `deploy/build.sh` e atualiza o código da Lambda via OIDC. Uma edição nova só sai na próxima
  execução; para publicar na hora, invoque `journal-build` à mão.
- **Camadas** (`tests/test_core_boundary.py` garante que `domain`, `ports` e `app` só importam a
  stdlib e umas às outras):
  - `domain/`: `Article` (title, url, summary, source, published_at, image\*, section, `body`, `kind`)
    e `Edition`.
  - `ports/`: `SourcePort`, `PublisherPort`, `HistoryPort`.
  - `app/`: `BuildJournal` (`app/build.py`, o fluxo inteiro em `run()`), `KeywordFilter` e
    `Sectioned` (aplica `section` e `kind` a qualquer fonte).
  - `adapters/`: `rss.py`, `static_site.py`, `s3.py`, `storage.py`.
  - `config.py` monta tudo a partir do `journal.toml`, com um registro de tipos de adaptador.
- **Dados úteis para o LLM:**
  - `Article.body`: o texto completo em HTML seguro, nas fontes com `full_text = true`. Mais da
    metade dos itens têm.
  - `Article.kind`: `noticia` ou `artigo`.
  - `Article.key`: identidade estável por URL.
- **Site:**
  - cada edição tem `index.html` (notícias) e `artigos.html` (artigos), com abas, índice de
    seções, menu lateral de edições e páginas por item em `articles/<id>.html`;
  - não há JavaScript nenhum;
  - o CSS tem o hash no nome do arquivo (`style.<hash>.css`), porque o CloudFront ignora a query
    string no cache.
- **Specs:** `openspec/specs/` tem 8 capacidades, todas válidas com `--strict`. Toda mudança segue
  propose → apply → archive, e as mudanças desta sessão estão em `openspec/changes/archive/`.

## 3. Restrições que valem para o LLM

1. **Só RSS:** nada de scraping, PDFs ou download de páginas (decisão de 2026-11-25, reconfirmada
   em 2026-11-26). O LLM trabalha só com o que os feeds mandam.
2. **Texto de feed é dado, nunca instrução.** O conteúdo dos feeds vai para o prompt e pode conter
   injeção de prompt. A saída do LLM nunca entra na página como HTML cru:
   - texto puro com `escape()`;
   - ou HTML passado pelo `body_html()` de `adapters/rss.py`, que só deixa passar uma lista de tags
     permitidas.
3. **Transparência** (README, "Uso responsável"):
   - todo texto gerado é identificado como IA, por exemplo "Texto gerado por IA a partir de: g1,
     Agência Brasil, The Guardian", com link para cada original;
   - nenhuma afirmação é atribuída a uma fonte que não a fez.
4. **Falha do LLM não derruba a edição.** Sem chave, sem orçamento, timeout ou erro da API, a
   edição sai como hoje, sem síntese, e o motivo vai para o log.
5. **O pacote da Lambda é só Python:** `deploy/build.sh` instala as dependências na máquina do
   build para um runtime arm64. O SDK oficial `anthropic` depende de `pydantic-core` e `jiter`,
   que são compilados, e isso quebra o pacote. Duas saídas:
   - chamar a API com `urllib`, só com a stdlib, o que mantém o pacote como está;
   - mudar o build para baixar as wheels da plataforma da Lambda
     (`uv pip install --python-platform aarch64-manylinux2014 …`) e testar o pacote no CI.
6. **Chave da API no SSM**, num `SecureString` como `/journal/anthropic-api-key`, lida em tempo de
   execução:
   - o boundary do projeto já permite `ssm:GetParameter` em `parameter/journal/*` e o `kms:Decrypt`
     via SSM;
   - a chave nunca vai para o `journal.toml`, para variável do Terraform em texto nem para o
     repositório, que é **público**.
7. **Custo e tempo:**
   - uma edição busca cerca de 1.000 itens; medido em 2026-11-26, 563 estavam na janela de 2
     dias (491 notícias, 72 artigos), antes de descontar o que edições anteriores já publicaram;
   - a Lambda tem 600 s;
   - é preciso um orçamento por edição (número máximo de chamadas ou de tokens) e um cache por
     `Article.key`, para que revisões no mesmo dia não paguem de novo pelo mesmo texto. O cache
     pode ficar no próprio storage, como `llm-cache/<key>.json`.
8. **Modelo (decidido em 2026-11-26):** DeepSeek, `deepseek-flash` sem raciocínio, chamado com
   `urllib` (`adapters/deepseek.py`), o que resolve o item 5 sem dependência nova. Orçamento: até
   US$ 5/mês. Confira preços em <https://api-docs.deepseek.com/quick_start/pricing> antes de
   mudar limites; não decida de memória.

## 4. Desenho proposto (para virar proposta no OpenSpec)

Divida em mudanças pequenas, na ordem abaixo; cada uma entrega algo visível.

### 4.1 Aquecimento dos artigos (a primeira, e a menor)
- **Porta** `SummarizerPort.warmup(article) -> str | None` em `ports/`, com o adaptador do LLM em
  `adapters/` e uma fake em `tests/fakes.py`.
- **Domínio:** `Article.warmup: str | None`, em texto puro.
- **Fluxo:** em `BuildJournal.run()`, depois da seleção, uma chamada por item de `kind = "artigo"`
  com cache por `key`. A entrada é `body` ou `summary`; o papel do arXiv é o próprio resumo.
- **Site:**
  - em `artigos.html`, o parágrafo aparece no lugar do resumo do feed;
  - na página do artigo, aparece acima do texto completo, com o selo de IA;
  - **o resto não muda.**
- Serve para testar chave, custo, cache, timeout e falha com risco quase zero.

### 4.2 Agrupar as notícias por história
- **Entrada:** todas as notícias da janela, depois da dedup e do histórico, **sem** o limite por
  seção.
- **Saída:** grupos de itens sobre o mesmo fato. Dá para fazer com o LLM (títulos e resumos numa
  só chamada, devolvendo grupos de ids), com embeddings ou com os dois.
- **Domínio:** uma entidade `Story`, com título, seção, `items: tuple[Article, ...]` e os campos
  do §4.3.
- **Ranking:** escolher **as 10 histórias** da edição. Critério a definir (§6).

### 4.3 Síntese de cada história
- **Saída estruturada** (JSON), com:
  - título;
  - texto em pt-BR numa voz única, em parágrafos;
  - para cada parágrafo ou afirmação, os ids dos itens que a sustentam;
  - uma lista de **divergências**, com a afirmação, quem diz o quê e os ids.
- **Validação:** cada id citado existe no grupo, e todo item do grupo aparece nos créditos. Uma
  segunda passada pode checar se cada afirmação está no texto das fontes.
- Fontes em inglês (Guardian, NASA, 404 Media, Ars) são traduzidas na síntese.

### 4.4 Site com histórias
- `index.html` lista as 10 histórias, cada uma com título, um trecho, as fontes e um selo
  "divergência" quando houver.
- Página da história: o texto, o bloco de divergências e a lista de fontes com link para cada
  original e para a página do item.
- `articles.json` ganha um `stories.json` irmão. `seen.json` marca como publicados todos os itens
  das histórias que saíram.
- A página de Artigos não muda, além do aquecimento do §4.1.

### 4.5 Visão do dono, 2026-11-27: "um jornal de verdade"

O dono não se sente lendo um jornal. A ideia dele:

- **Menos fontes, tudo do dia:** poucas fontes que cobrem os mesmos assuntos, lidas por inteiro.
  As repetições entre elas são o sinal do que importa. O corte (`max_per_section`) passa a valer
  **depois** de agrupar, nunca antes.
- **Número fixo de assuntos:** agrupar as repetições, escolher N histórias e publicar cada uma
  como **um artigo só**, escrito pelo LLM numa voz única e com conferência de fatos.
- **Diagramação de jornal:** uma capa com manchete e imagem grande, chamadas médias e notas sem
  imagem. As seções vêm em faixas, rolando a página para baixo. As imagens são as que os feeds
  mandam.

Limites a levar em conta:

- **O RSS não traz "tudo do dia".** Cada feed tem só os últimos 10 a 50 itens. Para cobrir o dia,
  a escolha das fontes precisa olhar quanto elas se repetem entre si.
- **A conferência confere contra as fontes, não contra o mundo.** O que ela verifica: cada
  afirmação está em pelo menos um item do grupo e as divergências aparecem (§4.3). Ela não
  verifica se o fato é verdade.
- **Imagem só a do feed**, com crédito (sem scraping). Algumas vêm pequenas, então a diagramação
  precisa funcionar sem foto.

Decidido em 2026-11-27:

- **Temas fixos:** política, economia e tecnologia.
- **Fontes:** revisar e provavelmente reduzir, escolhendo as que se repetem.
- **Primeiro o "backend"**, local, com testes e fakes, sem chamar a DeepSeek à toa. A
  diagramação e o jornal de referência vêm depois.
- **Regra das fontes (2026-11-28):** o feed precisa mandar o texto completo e o site não pode ter
  paywall de nenhum tipo, nem o medido, que libera algumas matérias por mês. "Ler na fonte" tem que
  abrir sempre. Na conferência, a página aberta, sem login, precisa ter o texto do feed e nenhuma
  marcação de bloqueio (`content_tier` metered/locked, `paywall: ativo`, `meteringExpires`,
  `tipo-paywall`, `isAccessibleForFree: false`).
- **Fontes de Política:** g1 política e CNN Brasil (grande imprensa), JOTA (STF, Congresso e
  governo; as notícias são abertas, e o JOTA PRO é um produto à parte), Jovem Pan (direita) e
  Revista Fórum (esquerda), para ter contraste. Foram medidas em 2026-11-27/28. A CNN Brasil e a
  Jovem Pan só têm feed geral, com esportes e variedades, e entram filtradas pelo endereço do
  link (`/politica/`). A Fórum, a CNN e a Jovem Pan guardam de 1,5 h a 6 h no feed, então
  precisam do coletor de hora em hora. Recusadas: O Antagonista (em 2026-11-28 o feed passou a
  mandar só ~300 caracteres; vale medir de novo), Veja e Estadão (paywall medido), Congresso em
  Foco, Brasil de Fato, DW, UOL e Estado de Minas (só resumo; puxar a página seria scraping),
  Agência Brasil, Poder360 e Brasil 247 (escolha do dono; a Agência Brasil política tem texto
  completo, mas publica ~3 por dia e é a voz oficial do governo), Folha, Gazeta do Povo e
  CartaCapital (paywall e sem texto no feed), Agência Câmara (quase não repete as outras),
  Metrópoles (sem seção de política no feed), JB (bloqueia leitores automáticos), R7, SBT News,
  O Tempo, Diário do Nordeste, Band e Correio Braziliense (sem feed que funcione), El País (a
  edição em português acabou em 2021).
- **Fontes de Economia:** g1 economia e CNN Brasil (grande imprensa; a CNN filtrada por
  `/economia/`, porque as categorias dela variam), InfoMoney, Money Times (quase tudo dele também
  sai em outra fonte), Seu Dinheiro e Jovem Pan (`/economia/`, para o contraste de espectro).
  Todas grátis e com texto completo, medidas em 2026-11-28. InfoMoney e Money Times guardam
  6–7 h, então também dependem do coletor. Recusadas: Estadão, Veja e Valor (paywall medido; o
  Valor também tem ~22% de patrocinado), Exame, NeoFeed, O Antagonista economia e Gazeta do Povo
  (só resumo), Le Monde Diplomatique e Fórum economia (feed bloqueado), Brazil Journal, Bloomberg
  Línea e Outras Palavras (quase não repetem as outras).
- **Filtro por endereço (a fazer):** uma opção por fonte, por exemplo `paths = ["/politica/"]`,
  que só aceita itens cujo link começa por um desses caminhos. Ela deixa usar o mesmo feed geral
  em mais de uma seção. Entra junto com o coletor. O endereço é melhor que a categoria do feed: a
  CNN marca `Política` em todas as matérias de política, mas as de economia vêm com categorias
  diferentes.
- **Tecnologia (aberto):** HN, Lobsters, Techmeme e Tildes mandam só título e link. A proposta é
  usar as APIs oficiais do HN e do Lobsters como curadoria, com o LLM resumindo a discussão, mais
  Techdirt e Pluralistic para ter texto completo. Isso depende de o dono aceitar "RSS ou API
  oficial" no lugar de "só RSS".
- **Internacional (futuro):** Opera Mundi é candidata.

## 5. Ordem sugerida das mudanças

1. ~~Aquecimento dos artigos (§4.1)~~: feito em 2026-11-26
   (`openspec/changes/archive/2026-11-26-add-article-warmup/`). Porta `SummarizerPort`,
   cache em `llm-cache/warmup/`, orçamento em `[summarizer]`, chave em
   `/journal/deepseek-api-key`.
2. Agrupamento e ranking, mostrando só "3 fontes cobrem isto", sem texto novo.
3. Síntese com citações.
4. Divergências em destaque.

## 6. Perguntas em aberto para o dono do projeto

Decididas em 2026-11-27:

- **Ranking das 10 histórias:** mais fontes cobrindo primeiro, mas com pelo menos uma por seção
  (Brasil e mundo, Ciência, Tecnologia, RS) quando houver.
- **Contradições:** inline no parágrafo ("segundo A…; B afirma…") e um selo "divergência" na
  lista. O LLM nunca decide quem está certo.
- **História de uma fonte só:** entra entre as 10, reescrita na mesma voz; as de mais fontes vêm
  antes.
- **Os itens originais:** a capa mostra as 10 histórias e um link abre a lista "todas as notícias
  da edição", como é hoje.
- **Voz única:** todo texto escrito pelo LLM (histórias e aquecimentos) soa como o mesmo autor.
  Exemplo de teste: Dino suspende emendas de Flávio Bolsonaro, coberto por O Sul e Rádio Guaíba
  em 2026-11-27 (revisão 3).
- ~~Orçamento mensal~~ e ~~modelos~~: decididos (§3.8).

## 7. Pendências sem LLM

- **Curadoria:**
  - o resumo do APOD da NASA vem poluído com o menu do site;
  - muitos posts do Simon Willison são notas curtas;
  - g1, NASA e Rádio Guaíba dominam a própria seção; isso deixa de importar quando as notícias
    virarem 10 histórias.
- **Artigos:** a seleção ainda é por recência. O arXiv entra pela ordem do feed, porque todos os
  papers do dia têm o mesmo horário. A regra de relevância para artigos fica para depois do §4.1.
- **Infra:** alerta de falha (alarme do CloudWatch por e-mail) e domínio próprio, deixados para
  depois.
- **Fora do repositório:** `~/Coding/aws-account` não é versionado; o projeto `memorization` tem
  um desvio de handler (`index.handler` vs `lambda.handler`) que impede um `tofu apply` completo.

## 8. Como trabalhar neste repositório

- **OpenSpec:** `openspec new change <nome>`, artefatos (proposta, specs delta, design, tarefas),
  implementação, `openspec archive <nome> --yes`, `openspec validate --specs --strict`.
  Requisitos acima de 500 caracteres falham no `--strict`; um bloco MODIFIED repete o requisito
  inteiro, com todos os cenários.
- **Commits:** em inglês, terminando com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **AWS local:** use o perfil `agent` (papel temporário de 1 h, assumido a partir do usuário
  `admin` com `aws login`). O OpenTofu não lê perfis `login_session`; exporte antes:
  `eval "$(aws configure export-credentials --profile agent --format env)"; unset AWS_PROFILE`.
  Operações destrutivas ou de root vão para o dono do projeto como script.
- **Prévia local:** copie o `journal.toml` trocando o storage para `local`, rode
  `uv run journal build --config <cópia>` e abra as páginas geradas. Para capturas, use o Chrome
  headless com `--user-data-dir` novo, para não pegar cache.
- **Publicar depois do deploy:** `aws lambda invoke --function-name journal-build …`. A resposta
  traz `published`, `fetched` e `source_errors`.
