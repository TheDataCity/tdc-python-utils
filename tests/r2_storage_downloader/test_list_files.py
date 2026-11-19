import os

import pytest

from tdc_python_utils.r2_storage_downloader import R2StorageDownloader

# These tests read the live global-data bucket. Importing the module above loads .env first.
pytestmark = pytest.mark.skipif(
    not all(
        os.getenv(name)
        for name in ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_ACCOUNT_ID")
    ),
    reason="needs R2 credentials",
)


def test_list_objects():
    c = 0
    for i, j in R2StorageDownloader(
        bucket="global-data", container_name="creditsafe/output"
    ).list_objects():
        assert i
        assert j
        c += 1
    assert c > 0
