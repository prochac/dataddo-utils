import pyarrow as pa
import pyarrow.ipc
import requests

__DEFAULT_HOST = "https://api.dataddo.com"
__API_VERSION = "v1.0"
__ENDPOINT_PATH = "/get/"
__SOURCE_PATH = "/get/source/"
__FLOW_PATH = "/get/flow/"

ARROW_STREAM_MIME = "application/vnd.apache.arrow.stream"

_HEX_CHARS = frozenset("0123456789abcdefABCDEF")


def _is_hex(s: str) -> bool:
    return all(c in _HEX_CHARS for c in s)


class Token(str):
    def __init__(self, token: str | None):
        if token is None:
            raise ValueError("Token must be specified")
        if len(token) != 64 or not _is_hex(token):
            raise ValueError("Token must be 64 hexadecimal characters")


class _ObjectID(str):
    def __init__(self, value: str | None):
        if value is None:
            raise ValueError("ObjectID must be specified")
        if len(value) != 24 or not _is_hex(value):
            raise ValueError("ObjectID must be 24 hexadecimal characters")


class FlowID(_ObjectID):
    pass


class SourceID(_ObjectID):
    pass


class EndpointID(_ObjectID):
    pass


def get_source_data(
    token: Token,
    id: SourceID | EndpointID | FlowID,
    host: str | None = None,
) -> pa.Table:
    """Fetch data from Dataddo as an Apache Arrow table."""
    with requests.get(
        _build_url(host or __DEFAULT_HOST, id),
        params={"type": "arrow"},
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
    ) as resp:
        resp.raise_for_status()
        ct = resp.headers.get("Content-Type", "")
        if not ct.startswith(ARROW_STREAM_MIME):
            raise ValueError(f"Expected {ARROW_STREAM_MIME}, got {ct}")
        with pa.ipc.open_stream(resp.raw) as reader:
            return reader.read_all()


def _build_url(host: str, id: SourceID | EndpointID | FlowID) -> str:
    api_url = f"{host}/{__API_VERSION}"
    if isinstance(id, SourceID):
        return api_url + __SOURCE_PATH + str(id)
    if isinstance(id, EndpointID):
        return api_url + __ENDPOINT_PATH + str(id)
    if isinstance(id, FlowID):
        return api_url + __FLOW_PATH + str(id)
    raise TypeError("id must be SourceID, EndpointID, or FlowID")
