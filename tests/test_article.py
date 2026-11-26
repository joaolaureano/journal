import dataclasses
import re
from datetime import UTC, datetime

import pytest

from journal.domain import Article

WHEN = datetime(2026, 1, 1, tzinfo=UTC)


def make(**overrides):
    values = {
        "title": "Title",
        "url": "https://example.com/a",
        "summary": "Summary",
        "source": "example",
        "published_at": WHEN,
    }
    return Article(**(values | overrides))


def test_fields_are_kept_as_given():
    a = make()
    assert (a.title, a.url, a.summary, a.source, a.published_at) == (
        "Title",
        "https://example.com/a",
        "Summary",
        "example",
        WHEN,
    )
    assert a.id


def test_empty_summary_is_allowed():
    assert make(summary="").summary == ""


def test_same_url_same_id():
    assert make(title="A", source="x").id == make(title="B", source="y").id


def test_different_url_different_id():
    assert make(url="https://example.com/a").id != make(url="https://example.com/b").id


def test_id_is_lowercase_hex():
    assert re.fullmatch(r"[0-9a-f]+", make().id)


@pytest.mark.parametrize("title", ["", "   "])
def test_blank_title_rejected(title):
    with pytest.raises(ValueError):
        make(title=title)


@pytest.mark.parametrize(
    "url", ["/relative", "ftp://example.com/a", "https://", "example.com"]
)
def test_non_http_url_rejected(url):
    with pytest.raises(ValueError):
        make(url=url)


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):
        make(published_at=datetime(2026, 1, 1))


def test_article_is_immutable():
    a = make()
    with pytest.raises(dataclasses.FrozenInstanceError):
        a.title = "Other"
    assert a.title == "Title"


def test_image_is_optional():
    assert make().image is None
    assert make(image="https://cdn.example.com/a.jpg").image == (
        "https://cdn.example.com/a.jpg"
    )


@pytest.mark.parametrize("image", ["javascript:alert(1)", "/a.jpg", "data:image/png,x"])
def test_non_http_image_rejected(image):
    with pytest.raises(ValueError):
        make(image=image)


def test_image_caption_and_credit():
    a = make(
        image="https://cdn.example.com/a.jpg",
        image_caption="Dimorphos",
        image_credit="ESA",
    )
    assert (a.image_caption, a.image_credit) == ("Dimorphos", "ESA")
    assert (make().image_caption, make().image_credit) == (None, None)
