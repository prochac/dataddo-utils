import os

import pyarrow as pa
import pytest

from dataddo.data_api import (
    EndpointID,
    FlowID,
    SourceID,
    Token,
    _build_url,
    get_source_data,
)


class TestToken:
    def test_valid(self):
        Token("a" * 64)

    def test_mixed_case_hex(self):
        Token("aF" * 32)

    @pytest.mark.parametrize("value", ["a" * 63, "a" * 65, ""])
    def test_wrong_length(self, value):
        with pytest.raises(ValueError):
            Token(value)

    def test_non_hex(self):
        with pytest.raises(ValueError):
            Token("z" * 64)

    def test_none(self):
        with pytest.raises(ValueError):
            Token(None)


@pytest.mark.parametrize("cls", [SourceID, EndpointID, FlowID])
class TestObjectID:
    def test_valid(self, cls):
        cls("a" * 24)

    def test_wrong_length(self, cls):
        with pytest.raises(ValueError):
            cls("a" * 23)

    def test_non_hex(self, cls):
        with pytest.raises(ValueError):
            cls("z" * 24)


class TestBuildURL:
    def test_source(self):
        assert (
            _build_url(
                "https://api.dataddo.com",
                SourceID("a" * 24),
            )
            == f"https://api.dataddo.com/v1.0/get/source/{'a' * 24}"
        )

    def test_endpoint(self):
        assert (
            _build_url(
                "https://api.dataddo.com",
                EndpointID("b" * 24),
            )
            == f"https://api.dataddo.com/v1.0/get/{'b' * 24}"
        )

    def test_flow(self):
        assert (
            _build_url(
                "https://api.dataddo.com",
                FlowID("c" * 24),
            )
            == f"https://api.dataddo.com/v1.0/get/flow/{'c' * 24}"
        )

    def test_unknown_id_type(self):
        with pytest.raises(TypeError):
            _build_url("https://api.dataddo.com", "not-an-id")  # ty: ignore[invalid-argument-type]


# Integration tests — skipped unless DATADDO_TOKEN + DATADDO_SOURCE_ID are set.
# DATADDO_HOST is optional and falls back to the production default.


def _env_or_skip(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        pytest.skip(f"{name} not set")
    return val


@pytest.fixture
def token() -> Token:
    return Token(_env_or_skip("DATADDO_TOKEN"))


@pytest.fixture
def source_id() -> SourceID:
    return SourceID(_env_or_skip("DATADDO_SOURCE_ID"))


@pytest.fixture
def host() -> str | None:
    return os.environ.get("DATADDO_HOST")


def test_get_source_data_returns_arrow_table(token, source_id, host):
    table = get_source_data(token, source_id, host=host)
    assert isinstance(table, pa.Table)
    assert table.num_columns > 0
    assert table.num_rows >= 0
    # Schema is self-describing on the wire — sanity-check it's intact.
    assert len(table.schema.names) == table.num_columns
