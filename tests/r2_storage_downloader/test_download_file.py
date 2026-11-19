import os
from pathlib import Path

import pytest
from loguru import logger

from tdc_python_utils.r2_storage_downloader import R2StorageDownloader

# These tests read the live global-data bucket. Importing the module above loads .env first.
pytestmark = pytest.mark.skipif(
    not all(
        os.getenv(name)
        for name in ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_ACCOUNT_ID")
    ),
    reason="needs R2 credentials",
)


def test_download_file():
    R2StorageDownloader(
        bucket="global-data", container_name="creditsafe/output"
    ).download_file(target_blob="WebsiteInfo.csv", local_dir="tests", force=True)

    logger.info("Removing test download")

    p = Path("tests/WebsiteInfo.csv")

    assert p.exists()

    p.unlink()
