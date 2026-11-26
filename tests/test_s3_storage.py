import io

import pytest
from fakes import article, edition

from journal.adapters.s3 import LONG_CACHE, SHORT_CACHE, S3Storage
from journal.adapters.static_site import StaticSitePublisher
from journal.adapters.storage import StoragePort
from journal.ports import PublishError


class ClientError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


class FakeS3:
    """The few boto3 S3 client calls S3Storage uses, kept in memory."""

    def __init__(self):
        self.objects: dict[tuple[str, str], dict] = {}

    def head_object(self, Bucket, Key):
        if (Bucket, Key) not in self.objects:
            raise ClientError("404")
        return {}

    def get_object(self, Bucket, Key):
        if (Bucket, Key) not in self.objects:
            raise ClientError("NoSuchKey")
        return {"Body": io.BytesIO(self.objects[(Bucket, Key)]["Body"])}

    def put_object(self, **kwargs):
        self.objects[(kwargs["Bucket"], kwargs["Key"])] = kwargs


@pytest.fixture
def s3():
    return FakeS3()


def test_is_a_storage(s3):
    assert isinstance(S3Storage("b", client=s3), StoragePort)


def test_round_trip_with_prefix(s3):
    storage = S3Storage("b", prefix="/site/", client=s3)
    assert not storage.exists("a.html") and storage.read("a.html") is None
    storage.write("a.html", b"<p>")
    assert storage.exists("a.html") and storage.read("a.html") == b"<p>"
    assert ("b", "site/a.html") in s3.objects


def test_content_type_and_cache(s3):
    storage = S3Storage("b", client=s3)
    storage.write("index.html", b"")
    storage.write("edicoes/2026-11-26/index.html", b"")
    storage.write("style.css", b"")
    storage.write("editions.json", b"")
    storage.write("artigos.html", b"")
    storage.write("edicoes/2026-11-26/artigos.html", b"")
    obj = {k: v for (_, k), v in s3.objects.items()}
    assert obj["index.html"]["ContentType"] == "text/html; charset=utf-8"
    assert obj["index.html"]["CacheControl"] == SHORT_CACHE
    assert obj["edicoes/2026-11-26/index.html"]["CacheControl"] == LONG_CACHE
    assert obj["style.css"]["ContentType"] == "text/css; charset=utf-8"
    assert obj["editions.json"]["ContentType"] == "application/json; charset=utf-8"
    assert obj["editions.json"]["CacheControl"] == SHORT_CACHE
    assert obj["artigos.html"]["CacheControl"] == SHORT_CACHE
    assert obj["edicoes/2026-11-26/artigos.html"]["CacheControl"] == LONG_CACHE


def test_other_errors_become_publish_errors(s3):
    def denied(**_kwargs):
        raise ClientError("AccessDenied")

    s3.head_object = denied
    s3.put_object = denied
    storage = S3Storage("b", client=s3)
    with pytest.raises(PublishError, match="AccessDenied"):
        storage.exists("x")
    with pytest.raises(PublishError, match="s3://b/x"):
        storage.write("x", b"")


def test_static_site_publishes_to_s3(s3):
    publisher = StaticSitePublisher(S3Storage("b", client=s3))
    publisher.publish(edition(article()))
    publisher.publish(edition(article("https://a.com/2")))
    keys = {k for _, k in s3.objects}
    assert {"index.html", "editions.json", "seen.json", "style.css"} <= keys
    assert "edicoes/2026-11-26/index.html" in keys
    assert "edicoes/2026-11-26-2/index.html" in keys
