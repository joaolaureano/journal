import pytest
from fakes import article, edition

from journal.domain import Story


def test_id_depends_only_on_the_items():
    a, b = (
        article("https://a.com/1", source="A"),
        article("https://b.com/2", source="B"),
    )
    assert Story((a, b)).id == Story((b, a), "Política").id
    assert Story((a,)).id != Story((a, b)).id


def test_lead_and_distinct_sources():
    a = article("https://a.com/1", source="g1")
    b = article("https://a.com/2", source="g1")
    c = article("https://c.com/3", source="JOTA")
    story = Story((a, b, c))
    assert story.lead == a and story.sources == ("g1", "JOTA")


def test_story_needs_an_item():
    with pytest.raises(ValueError):
        Story(())


def test_edition_has_no_stories_by_default():
    assert edition().stories == ()
