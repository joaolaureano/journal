import pytest
from fakes import article

from journal.app import KeywordFilter


@pytest.mark.parametrize(
    "include, exclude, title, summary, expected",
    [
        (["selic"], [], "Copom mantém a Selic", "", True),
        (["selic"], [], "Time vence clássico", "", False),
        (["inflacao"], [], "Economia", "Alta da INFLAÇÃO assusta", True),
        (["Inflação"], [], "inflacao recua", "", True),
        (["juros"], [], "Conjuros antigos", "", False),
        (["banco central"], [], "O Banco   Central decide", "", True),
        (["banco"], ["futebol"], "Banco patrocina time de futebol", "", False),
        ([], ["futebol"], "Bolsa sobe", "", True),
        ([], [], "Qualquer coisa", "", True),
        (["c++"], [], "Novidades do C++ 26", "", True),
    ],
)
def test_keyword_filter(include, exclude, title, summary, expected):
    f = KeywordFilter(include, exclude)
    assert f.matches(article(title=title, summary=summary)) is expected


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://www1.folha.uol.com.br/mercado/x.shtml", False),
        ("https://FOLHA.uol.com.br/x", False),
        ("https://redir.folha.com.br/redir/x", False),
        ("https://noticias.uol.com.br/x", True),
        ("https://minhafolha.com.br/x", True),  # same letters, not a subdomain
    ],
)
def test_excluded_domains(url, expected):
    f = KeywordFilter(exclude_domains=["folha.uol.com.br", "folha.com.br"])
    assert f.matches(article(url=url)) is expected
