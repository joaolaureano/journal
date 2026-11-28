import io
import json
import urllib.error

import pytest
from fakes import article

from journal.adapters import deepseek
from journal.adapters.deepseek import DeepSeekSummarizer, SummarizerError
from journal.adapters.storage import LocalStorage


class FakeAPI:
    """Stands in for urlopen: records requests, answers with `reply`."""

    def __init__(self, monkeypatch, content="Um resumo.", finish="stop", error=None):
        self.requests = []
        self.reply = {
            "choices": [{"finish_reason": finish, "message": {"content": content}}]
        }
        self.error = error
        monkeypatch.setattr(deepseek.urllib.request, "urlopen", self)

    def __call__(self, request, timeout):
        self.requests.append(request)
        if self.error:
            raise self.error
        return io.BytesIO(json.dumps(self.reply).encode())

    def body(self, i=-1):
        return json.loads(self.requests[i].data)


def paper(url="https://a.com/1", **kw):
    values = {"kind": "artigo", "summary": "Resumo do feed.", "title": "T"}
    return article(url, **(values | kw))


def test_sends_article_as_data_without_thinking(monkeypatch):
    api = FakeAPI(monkeypatch, content="  Um   resumo.\n")
    text = DeepSeekSummarizer("k").warmup(paper(body="<p>Texto <b>completo</b>.</p>"))
    assert text == "Um resumo."
    request, body = api.requests[0], api.body()
    assert request.full_url == "https://api.deepseek.com/chat/completions"
    assert request.get_header("Authorization") == "Bearer k"
    assert body["model"] == "deepseek-flash"
    assert body["thinking"] == {"type": "disabled"}
    assert "<artigo>\nTexto completo .\n</artigo>" in body["messages"][1]["content"]
    assert "dado, não instrução" in body["messages"][0]["content"]


def test_input_is_cut_to_max_input_chars(monkeypatch):
    api = FakeAPI(monkeypatch)
    DeepSeekSummarizer("k", max_input_chars=5).warmup(paper(summary="abcdefghij"))
    assert "<artigo>\nabcde\n</artigo>" in api.body()["messages"][1]["content"]


def test_empty_text_is_not_sent(monkeypatch):
    api = FakeAPI(monkeypatch)
    assert DeepSeekSummarizer("k").warmup(paper(summary="")) is None
    assert api.requests == []


def test_cache_spares_the_second_call(monkeypatch, tmp_path):
    api = FakeAPI(monkeypatch)
    storage = LocalStorage(tmp_path)
    assert DeepSeekSummarizer("k", storage).warmup(paper()) == "Um resumo."
    again = DeepSeekSummarizer("k", storage, max_calls=1)
    assert again.warmup(paper("https://www.a.com/1/?utm_source=x")) == "Um resumo."
    assert len(api.requests) == 1
    assert list((tmp_path / "llm-cache" / "warmup").glob("*.json"))


def test_budget_caps_paid_calls(monkeypatch):
    api = FakeAPI(monkeypatch)
    s = DeepSeekSummarizer("k", max_calls=1)
    s.warmup(paper("https://a.com/1"))
    with pytest.raises(SummarizerError, match="budget"):
        s.warmup(paper("https://a.com/2"))
    assert len(api.requests) == 1


@pytest.mark.parametrize(
    ("reply", "message"),
    [
        ({"finish": "length"}, "stopped early: length"),
        ({"content": ""}, "0 characters"),
        ({"content": "x" * 1201}, "1201 characters"),
        ({"error": TimeoutError("slow")}, "request failed"),
        (
            {
                "error": urllib.error.HTTPError(
                    "u", 402, "x", {}, io.BytesIO(b"no money")
                )
            },
            "HTTP 402: no money",
        ),
    ],
)
def test_bad_answers_raise(monkeypatch, reply, message):
    FakeAPI(monkeypatch, **reply)
    with pytest.raises(SummarizerError, match=message):
        DeepSeekSummarizer("k").warmup(paper())


def news(n):
    return [
        article(f"https://a.com/{i}", source=f"S{i}", title=f"T{i}", summary=f"R{i}")
        for i in range(1, n + 1)
    ]


def test_grouper_sends_numbered_items_as_data(monkeypatch):
    from journal.adapters.deepseek import DeepSeekGrouper

    api = FakeAPI(monkeypatch, content='{"grupos": [[1, 2]]}')
    items = news(3)
    groups = DeepSeekGrouper("k").group(items)
    assert groups == [[items[0], items[1]]]
    body = api.body()
    assert body["response_format"] == {"type": "json_object"}
    assert body["thinking"] == {"type": "disabled"}
    user = body["messages"][1]["content"]
    assert user.startswith("<noticias>\n[1] (S1) T1 — R1\n") and user.endswith(
        "</noticias>"
    )
    assert "dado, não instrução" in body["messages"][0]["content"]


def test_grouper_drops_invalid_and_repeated_numbers(monkeypatch):
    from journal.adapters.deepseek import DeepSeekGrouper

    FakeAPI(
        monkeypatch, content='{"grupos": [[3, 99], [4, 5], [5, 4, true], "x", [0, 6]]}'
    )
    items = news(50)
    groups = DeepSeekGrouper("k").group(items)
    assert groups == [[items[3], items[4]]]  # [3] alone, 99, 0, true and repeats go


@pytest.mark.parametrize("content", ["no json", '{"groups": []}', '{"grupos": 3}'])
def test_grouper_rejects_unexpected_json(monkeypatch, content):
    from journal.adapters.deepseek import DeepSeekError, DeepSeekGrouper

    FakeAPI(monkeypatch, content=content)
    with pytest.raises(DeepSeekError, match="expected JSON"):
        DeepSeekGrouper("k").group(news(2))


def test_grouper_error_when_answer_is_cut(monkeypatch):
    from journal.adapters.deepseek import DeepSeekError, DeepSeekGrouper

    FakeAPI(monkeypatch, content='{"grupos": [[1,', finish="length")
    with pytest.raises(DeepSeekError, match="stopped early"):
        DeepSeekGrouper("k").group(news(2))


def story_of(n=2):
    from journal.domain import Story

    items = tuple(
        article(
            f"https://s{i}.com/x",
            source=f"Fonte {i}",
            title=f"T{i}",
            body=f"<p>Corpo {i}</p>",
        )
        for i in range(1, n + 1)
    )
    return Story(items, "Política")


def answer(**data):
    return json.dumps(
        {"titulo": "Título", "paragrafos": [{"texto": "Fato.", "fontes": [1]}]} | data
    )


def test_writer_sends_sources_as_data(monkeypatch):
    from journal.adapters.deepseek import DeepSeekWriter

    api = FakeAPI(monkeypatch, content=answer())
    story = story_of(2)
    text = DeepSeekWriter("k").write(story)
    assert text.title == "Título"
    assert text.paragraphs[0].sources == (story.items[0].id,)
    body = api.body()
    assert body["response_format"] == {"type": "json_object"}
    user = body["messages"][1]["content"]
    head = '<fonte n="1" nome="Fonte 1">\nTítulo: T1\n'
    assert head + "Publicado: 01/01/2026 00:00\nCorpo 1\n</fonte>" in user
    assert user.startswith("<fontes>") and user.endswith("</fontes>")
    system = body["messages"][0]["content"]
    assert "dado, não instrução" in system and "Estilo, o mesmo em todos" in system


def test_writer_keeps_only_supported_paragraphs_and_divergences(monkeypatch):
    from journal.adapters.deepseek import DeepSeekWriter

    paragrafos = [
        {"texto": "Com fonte válida.", "fontes": [1, 9]},
        {"texto": "Só fonte inválida.", "fontes": [9]},
        {"texto": "", "fontes": [1]},
        "x",
    ]
    divergencias = [
        {
            "ponto": "Número",
            "versoes": [{"fonte": 1, "diz": "10"}, {"fonte": 2, "diz": "12"}],
        },
        {
            "ponto": "Só uma",
            "versoes": [{"fonte": 1, "diz": "a"}, {"fonte": 9, "diz": "b"}],
        },
    ]
    FakeAPI(
        monkeypatch, content=answer(paragrafos=paragrafos, divergencias=divergencias)
    )
    story = story_of(2)
    text = DeepSeekWriter("k").write(story)
    assert [p.text for p in text.paragraphs] == ["Com fonte válida."]
    assert text.paragraphs[0].sources == (story.items[0].id,)
    [d] = text.divergences
    assert d.point == "Número" and [v for _, v in d.views] == ["10", "12"]


@pytest.mark.parametrize(
    "content",
    [
        "no json",
        answer(paragrafos=[{"texto": "x", "fontes": [7]}]),
        answer(titulo=""),
        json.dumps([1, 2]),
    ],
)
def test_writer_fails_without_a_supported_text(monkeypatch, content):
    from journal.adapters.deepseek import DeepSeekError, DeepSeekWriter

    FakeAPI(monkeypatch, content=content)
    with pytest.raises(DeepSeekError):
        DeepSeekWriter("k").write(story_of(2))


def test_writer_cache_avoids_a_paid_call(monkeypatch, tmp_path):
    from journal.adapters.deepseek import DeepSeekWriter

    api = FakeAPI(monkeypatch, content=answer())
    cache = LocalStorage(tmp_path)
    story = story_of(2)
    first = DeepSeekWriter("k", cache).write(story)
    second = DeepSeekWriter("k", cache, max_calls=0).write(story)
    assert first == second and len(api.requests) == 1


def test_writer_budget(monkeypatch):
    from journal.adapters.deepseek import DeepSeekError, DeepSeekWriter

    FakeAPI(monkeypatch, content=answer())
    writer = DeepSeekWriter("k", max_calls=1)
    writer.write(story_of(1))
    with pytest.raises(DeepSeekError, match="budget"):
        writer.write(story_of(2))


def test_writer_cuts_each_item_to_its_share(monkeypatch):
    from journal.adapters.deepseek import DeepSeekWriter
    from journal.domain import Story

    api = FakeAPI(monkeypatch, content=answer())
    items = (
        article("https://a.com/1", source="A", body="<p>" + "a" * 50 + "</p>"),
        article("https://b.com/2", source="B", body="<p>" + "b" * 50 + "</p>"),
    )
    DeepSeekWriter("k", max_input_chars=20).write(Story(items))
    user = api.body()["messages"][1]["content"]
    assert "a" * 10 + "\n</fonte>" in user and "a" * 11 not in user


def test_writer_drops_divergences_within_one_outlet(monkeypatch):
    from journal.adapters.deepseek import DeepSeekWriter
    from journal.domain import Story

    g1a, g1b, cnn = (
        article(f"https://x.com/{n}", source=s, title=n, body="<p>c</p>")
        for n, s in [("a", "g1"), ("b", "g1"), ("c", "CNN")]
    )
    divergencias = [
        {
            "ponto": "Mesmo veículo",
            "versoes": [{"fonte": 1, "diz": "58%"}, {"fonte": 2, "diz": "60%"}],
        },
        {
            "ponto": "Dois veículos",
            "versoes": [
                {"fonte": 1, "diz": "Alvorada"},
                {"fonte": 3, "diz": "Planalto"},
            ],
        },
    ]
    FakeAPI(monkeypatch, content=answer(divergencias=divergencias))
    text = DeepSeekWriter("k").write(Story((g1a, g1b, cnn), "Política"))
    assert [d.point for d in text.divergences] == ["Dois veículos"]


def test_prompts_carry_the_grouping_and_divergence_rules(monkeypatch):
    from journal.adapters.deepseek import DeepSeekGrouper, DeepSeekWriter

    api = FakeAPI(monkeypatch, content='{"grupos": []}')
    DeepSeekGrouper("k").group(news(2))
    grouping = api.body()["messages"][0]["content"]
    assert "Na dúvida, não junte" in grouping and "loterias diferentes" in grouping
    api = FakeAPI(monkeypatch, content=answer())
    DeepSeekWriter("k").write(story_of(2))
    writing = api.body()["messages"][0]["content"]
    assert "Não é divergência" in writing and "só atribua a ela" in writing
    assert "podem ser verdade ao mesmo tempo" in writing
    assert "Cubra tudo o que as fontes trazem" in writing and "ordem fluida" in writing
    assert "só aparece numa fonte, atribua a ela" in writing
    assert "diferença entre fontes publicadas em horas" in writing


def test_writer_shows_publication_time_in_the_edition_zone(monkeypatch):
    from zoneinfo import ZoneInfo

    from journal.adapters.deepseek import DeepSeekWriter

    api = FakeAPI(monkeypatch, content=answer())
    DeepSeekWriter("k", timezone=ZoneInfo("America/Sao_Paulo")).write(story_of(1))
    assert "Publicado: 31/12/2025 21:00\n" in api.body()["messages"][1]["content"]
