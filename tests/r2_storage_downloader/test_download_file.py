from pathlib import Path

from loguru import logger

from src.tdc_python_utils.r2_storage_downloader import R2StorageDownloader


def test_download_file():
    R2StorageDownloader(container_name="creditsafe/output").download_file(
        target_blob="WebsiteInfo.csv", local_dir="tests", force=True
    )

    logger.info("Removing test download")

    p = Path("tests/WebsiteInfo.csv")

    assert p.exists()

    p.unlink()
