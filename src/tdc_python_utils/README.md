# tdc_python_utils

Brief utilities used across TDC projects. Small helpers for downloads,
timing, simple coloured output, path setup, DuckDB connections, and
loading zipped data into Polars.

## Modules

- **`azure_storage_downloader.py`**: `AzureStorageDownloader` — download blobs from an Azure container (progress bar).
- **`colours.py`**: `highlight_text`, `highlight_all` — wrap substrings or full messages with ANSI colour codes.
- **`date_handler.py`**: `DateHandler`, `now()` — simple date helpers (current date strings, previous month helpers).
- **`duckdb_connector.py`**: `DuckDBConnector` — helper to install/load DuckDB extensions and attach SQLite/MySQL databases.
- **`paths.py`**: `ROOT`, `RAW_DATA`, `PROCESSED_DATA`, `setup_paths()` — project path constants and directory creation helper.
- **`timer.py`**: `execution_time` — decorator that prints execution time (uses coloured output).
- **`url_downloader.py`**: `download_zipfile_from_url()` — download a ZIP from a URL with a progress bar and save locally.
- **`zip_to_polars.py`**: `zip_to_polars()` — load a single CSV or Parquet file from inside a ZIP into a Polars DataFrame.

## Quick examples

Import and use `zip_to_polars`:

```python
from tdc_python_utils.zip_to_polars import zip_to_polars

df = zip_to_polars("data/archive.zip", file_format="csv")
```

Download a ZIP from a URL:

```python
from tdc_python_utils.url_downloader import download_zipfile_from_url

download_zipfile_from_url("https://example.com/data.zip", "data/data.zip")
```

Use the timer decorator:

```python
from tdc_python_utils.timer import execution_time

@execution_time
def work():
    # do work
    return 123

work()
```

## Dependencies

Common runtime dependencies (see `pyproject.toml` for exact pins): `polars`, `requests`, `tqdm`, `colorama`, `azure-storage-blob`, `duckdb`, `python-dotenv`.

---
Generated concise docs for the package; see individual modules for more details and parameter options.
