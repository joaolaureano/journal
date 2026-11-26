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
