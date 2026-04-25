# prochac-dataddo-utils

A thin Python client for the [Dataddo](https://www.dataddo.com/) Data API. Fetches data via the Apache Arrow IPC stream endpoint and hands it back as a `pyarrow.Table`, ready for zero-copy use in Polars / Pandas / DuckDB / PyArrow.

> Distributed name on PyPI: `prochac-dataddo-utils`. Import name: `dataddo`.

## Installation

Currently published to **test PyPI** only. The `--extra-index-url` is required so `pip` can resolve `pyarrow` and `requests` from the real PyPI:

```bash
pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  prochac-dataddo-utils
```

Or with `uv`:

```bash
uv add --index https://test.pypi.org/simple/ prochac-dataddo-utils
```

Project page: https://test.pypi.org/project/prochac-dataddo-utils/

## Usage

```python
from dataddo.data_api import Token, SourceID, get_source_data

token = Token("...")              # 64 hex chars
source_id = SourceID("...")        # 24 hex chars (Mongo ObjectID)

table = get_source_data(token, source_id)   # returns pyarrow.Table
```

Convert to your dataframe of choice (zero-copy where possible):

```python
import polars as pl
df = pl.from_arrow(table)

# or
df = table.to_pandas()
```

### Endpoints, flows, sources

`get_source_data` dispatches on the ID type to hit the matching API path:

```python
from dataddo.data_api import EndpointID, FlowID, SourceID

get_source_data(token, SourceID("..."))     # /v1.0/get/source/<id>
get_source_data(token, EndpointID("..."))   # /v1.0/get/<id>
get_source_data(token, FlowID("..."))       # /v1.0/get/flow/<id>
```

### Targeting a non-production environment

```python
get_source_data(token, source_id, host="https://dpe.test.dataddo.com")
```

Defaults to `https://api.dataddo.com`.

## Requirements

- Python ≥ 3.11
- `pyarrow`, `requests` (installed automatically)

## Development

Workflow uses [`uv`](https://docs.astral.sh/uv/), [`ruff`](https://docs.astral.sh/ruff/), and [`ty`](https://github.com/astral-sh/ty):

```bash
uv sync                # install package + dev deps
uv run pytest          # run tests
uv run ruff check .    # lint
uv run ty check        # type check
uv build               # build sdist + wheel
```

The integration test in `tests/test_data_api.py` is skipped unless `DATADDO_TOKEN` and `DATADDO_SOURCE_ID` are set in the environment (`DATADDO_HOST` is optional).

## License

MIT — see [LICENSE](LICENSE).
