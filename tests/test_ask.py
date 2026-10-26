"""質問スクリプトのトークン使用量表示テスト（LLMもAPIキーも使わない）。"""

from types import SimpleNamespace

from app import ask


def _patch_generate_content(monkeypatch, response):
    class FakeModels:
        def generate_content(self, **kwargs):
            return response

    class FakeClient:
        def __init__(self, api_key):
            self.models = FakeModels()

    monkeypatch.setattr(ask.genai, "Client", FakeClient)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    _patch_generate_content(
        monkeypatch,
        SimpleNamespace(
            usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=34),
            text="回答",
        ),
    )

    assert ask.ask("質問") == "回答"
    output = capsys.readouterr().out
    assert "[入力トークン数] 12" in output
    assert "[出力トークン数] 34" in output


def test_ask_reports_unavailable_token_counts(monkeypatch, capsys):
    _patch_generate_content(monkeypatch, SimpleNamespace(usage_metadata=None, text="回答"))

    assert ask.ask("質問") == "回答"
    output = capsys.readouterr().out
    assert "[入力トークン数] 取得できませんでした" in output
    assert "[出力トークン数] 取得できませんでした" in output
