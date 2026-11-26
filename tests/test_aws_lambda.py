from pathlib import Path

from test_s3_storage import FakeS3

from journal import aws_lambda
from journal.adapters.s3 import S3Storage

FIXTURES = Path(__file__).parent / "fixtures"


def test_handler_builds_into_given_storage(tmp_path, monkeypatch):
    config = tmp_path / "journal.toml"
    config.write_text(
        '[[sources]]\ntype = "rss"\nname = "F"\n'
        f'url = "{(FIXTURES / "feed.xml").as_uri()}"\n'
        '[publisher]\ntype = "static-site"\n'
    )
    monkeypatch.setenv("JOURNAL_CONFIG", str(config))
    s3 = FakeS3()
    result = aws_lambda.handler({}, None, storage=S3Storage("b", client=s3))
    assert result["published"] > 0 and result["source_errors"] == []
    assert ("b", "index.html") in s3.objects
    assert not (tmp_path / "dist").exists()
