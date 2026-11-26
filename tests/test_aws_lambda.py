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


class FakeSSM:
    def __init__(self, value=None):
        self.value = value
        self.asked = []

    def get_parameter(self, Name, WithDecryption):
        self.asked.append((Name, WithDecryption))
        if self.value is None:
            raise RuntimeError("ParameterNotFound")
        return {"Parameter": {"Value": self.value}}


def test_key_read_from_ssm(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")  # restores the original at teardown
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    monkeypatch.setenv("JOURNAL_DEEPSEEK_KEY_PARAMETER", "/journal/deepseek-api-key")
    ssm = FakeSSM("secret")
    aws_lambda._load_deepseek_key(ssm)
    assert ssm.asked == [("/journal/deepseek-api-key", True)]
    assert aws_lambda.os.environ["DEEPSEEK_API_KEY"] == "secret"


def test_unreadable_key_only_logs(monkeypatch, caplog):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setenv("JOURNAL_DEEPSEEK_KEY_PARAMETER", "/journal/deepseek-api-key")
    aws_lambda._load_deepseek_key(FakeSSM())
    assert "DEEPSEEK_API_KEY" not in aws_lambda.os.environ
    assert "ParameterNotFound" in caplog.text
