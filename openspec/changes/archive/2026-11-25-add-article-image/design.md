# Design

## Decisions

- **Domínio:** `Article.image: str | None = None`, último campo, para não quebrar quem cria artigos sem imagem. Se presente, precisa ser URL absoluta http(s), a mesma regra do `url`.
- **Escolha da imagem no RSS:** a primeira URL http(s) válida, nesta ordem: `media:content` que seja imagem (`medium="image"`, `type` `image/*` ou sem tipo declarado), `media:thumbnail`, `enclosure` com `type` `image/*`. Uma imagem inválida é descartada sem descartar o artigo: a validação acontece no adapter, que é a fronteira com o dado externo.
- **Sem `<img>` do HTML do resumo:** a varredura dos feeds atuais mostrou ícones de redes sociais (Slashdot), logo e pixels 1×1 (Agência Brasil). Filtrar isso com heurística é frágil; fica de fora.
- **Hotlink, não cópia:** `<img src>` aponta para a URL original. Não há download, cache nem redimensionamento. Atributos: `alt=""` (a imagem acompanha o título, que já descreve a notícia), `loading="lazy"`, `referrerpolicy="no-referrer"` (alguns CDNs recusam hotlink com referer; também evita vazar a URL do site).
- **Site autocontido:** a regra de links relativos vale para páginas e CSS do próprio site. Imagens externas não são links de página; sem internet o site continua navegável, só sem fotos.
- **CSS:** miniatura à direita na lista (proporção fixa, `object-fit: cover`); na página do artigo, largura total com altura automática.

## Risks / Trade-offs

- Imagem pode sumir no site de origem: o navegador mostra um espaço vazio (alt vazio, sem ícone de texto).
- Direitos: a imagem continua servida pelo site de origem, junto do crédito da fonte e do link para a matéria. README registra isso em "Uso responsável".
