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
