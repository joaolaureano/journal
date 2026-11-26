import pytest
from fakes import FakePublisher, FakeSource, article, edition

from journal.ports import PublisherPort, PublishError, SourceError, SourcePort


def test_fake_source_satisfies_contract():
    items = [article("https://example.com/1"), article("https://example.com/2")]
    source = FakeSource(items)
    assert isinstance(source, SourcePort)
    assert source.fetch() == items


def test_object_without_fetch_is_not_a_source():
    assert not isinstance(object(), SourcePort)


def test_fake_publisher_satisfies_contract():
    items = [article("https://example.com/1"), article("https://example.com/2")]
    publisher = FakePublisher()
    assert isinstance(publisher, PublisherPort)
    publisher.publish(edition(*items))
    assert publisher.published == items


def test_source_failure_is_caught_as_source_error():
    class FailingSource:
        def fetch(self):
            raise SourceError("boom")

    with pytest.raises(SourceError):
        FailingSource().fetch()


def test_publish_failure_is_caught_as_publish_error():
    class FailingPublisher:
        def publish(self, edition):
            raise PublishError("disk full")

    with pytest.raises(PublishError):
        FailingPublisher().publish(edition())
