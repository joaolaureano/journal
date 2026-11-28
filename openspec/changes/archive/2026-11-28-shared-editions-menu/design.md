# Design

- **Por que iframe:** o site não usa scripts. Um `iframe` com `menu.html` é o jeito sem script de várias páginas mostrarem um conteúdo que muda depois que elas foram publicadas.
- **Marcação da edição atual:** cada página aponta para `menu.html#e-<pasta>`; cada item tem `id="e-<pasta>"`, e `li:target` recebe o destaque. O iframe ainda rola até a edição da página.
- **Links:** `<base target="_top">` no `menu.html`, para a edição abrir na janela e não dentro do menu.
- **Ordem de publicação:** `menu.html` é gravado com o arquivo de edições, antes do manifesto e da capa.
- **Páginas antigas:** o CSS mantém as regras do menu antigo (`nav.editions-menu p/ol/a`), que elas ainda usam.
