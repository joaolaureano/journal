# Design

- **Revisão decidida pelo publicador**, não pelo core: só ele sabe o que já existe. Próxima revisão = nº de entradas daquele dia no manifesto + 1, pulando qualquer pasta que já exista (manifesto perdido não causa sobrescrita).
- **Porta de armazenamento fica em `adapters/`**, não em `ports/`: quem a usa é o adapter do site estático, não o core. Chaves são caminhos POSIX relativos, o que mapeia direto para chaves do S3.
- **Atomicidade por arquivo** no local (arquivo temporário + `os.replace`); a consistência do site vem da ordem de gravação, que vale igual para S3.
- **Fuso no build**: `now()` continua injetável; a data é `now().astimezone(timezone).date()`. Horários dos artigos continuam exibidos em UTC (sem mudança nesta etapa).
