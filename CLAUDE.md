# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`prochac-dataddo-utils` is a thin Python client for the [Dataddo](https://www.dataddo.com/) Data API, intended for use in Jupyter notebooks alongside Polars / Pandas / PyArrow. The package's job is to make a single authenticated HTTP call and hand back an Apache Arrow table — nothing more.

Currently published to **test PyPI only** (https://test.pypi.org/project/prochac-dataddo-utils/).

## Commands

Workflow is `uv`-based (build backend remains `hatchling`).

```bash
uv sync                                      # install package + dev deps (creates .venv, uv.lock)
uv run pytest                                # all tests (integration tests skip unless env vars set)
uv run pytest tests/test_data_api.py::TestToken::test_valid   # single test
uv run ruff check .                          # lint
uv run ruff format .                         # format
uv run ty check                              # type check (Astral's ty)
uv build                                     # builds sdist + wheel into dist/
uv publish --publish-url https://test.pypi.org/legacy/        # test PyPI release
```

To exercise the integration test, export before running pytest:

```bash
DATADDO_TOKEN=<64-hex>          # bearer token
DATADDO_SOURCE_ID=<24-hex>      # source ObjectID
DATADDO_HOST=https://dpe.test.dataddo.com  # optional; defaults to https://api.dataddo.com
```

## Architecture

The public surface is intentionally narrow — one function:

```python
get_source_data(token: Token, id: SourceID | EndpointID | FlowID, host: str | None = None) -> pa.Table
```

Key design choices that span files:

- **Single Arrow path, no JSON/CSV.** The package previously parsed JSON/CSV into a `numpy`-backed `DataResponse`; that was deleted. The Dataddo `?type=arrow` endpoint returns `application/vnd.apache.arrow.stream`, which the client opens incrementally via `pa.ipc.open_stream(resp.raw)` (with `requests` `stream=True`) instead of buffering the full body. Callers convert to their dataframe of choice: `pl.from_arrow(table)`, `table.to_pandas()`, etc.

- **ID types are validated `str` subclasses.** `Token` (64 hex chars) and the three `_ObjectID` subclasses `SourceID` / `EndpointID` / `FlowID` (24 hex chars each) are distinct types so that `_build_url` can dispatch on them with `isinstance` to pick the matching API path (`/get/source/`, `/get/`, `/get/flow/`). They are nominally distinct even though they're all 24-hex Mongo ObjectIDs — keep them as separate classes; URL routing depends on it.

- **`host` is a parameter, not module-level config.** This is deliberate so tests (and users) can target alternate environments like `dpe.test.dataddo.com` without monkey-patching globals.

- **`pyarrow` is a hard dependency**, not optional. The audience is data folks who almost always already have it transitively through Polars/Pandas. Don't reintroduce optional-dep branching ("if pyarrow installed, do X").

## Conventions

- **Don't reintroduce removed surface area.** No `Format` / `JSONFormat` / `CSVDelimiter` enums, no `DataResponse` wrapper, no `numpy`. If a caller needs bytes or a different parse, they can wrap `get_source_data` themselves — it's a single HTTP call.
- **Ruff config** lives in `pyproject.toml` (`line-length = 100`, rules `E/F/I/UP/B/SIM`, double-quote strings). Run `ruff format` after edits.
- **Type hints model runtime behavior.** `Token.__init__` and `_ObjectID.__init__` declare `str | None` because they explicitly raise on `None` at runtime; the test suite asserts that.
- **Dev deps live in `[dependency-groups] dev`** (PEP 735), not `[project.optional-dependencies]`. Package consumers never install pytest/ruff/ty.
