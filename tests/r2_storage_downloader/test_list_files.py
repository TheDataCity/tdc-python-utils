from src.tdc_python_utils.r2_storage_downloader import R2StorageDownloader


def test_list_objects():
    c = 0
    for i, j in R2StorageDownloader(
        bucket="global-data", container_name="creditsafe/output"
    ).list_objects():
        assert i
        assert j
        c += 1
    assert c > 0
