"""Tests for :class:`tdc_python_utils.r2.R2Bucket`, against moto's in-memory S3."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from moto.core import DEFAULT_ACCOUNT_ID
from moto.s3.models import s3_backends

from tdc_python_utils.r2 import R2Bucket

R2_VARIABLES = [
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_ACCOUNT_ID",
    "R2_BUCKET",
    "R2_ENDPOINT_URL",
]

NSPL = "postcode-details/PostcodeDetails_NSPL"


def put(bucket: R2Bucket, key: str, body: bytes = b"") -> None:
    bucket.client.put_object(Bucket=bucket.name, Key=key, Body=body)


def read(bucket: R2Bucket, key: str) -> bytes:
    return bucket.client.get_object(Bucket=bucket.name, Key=key)["Body"].read()


def keys(bucket: R2Bucket) -> set[str]:
    response = bucket.client.list_objects_v2(Bucket=bucket.name)
    return {obj["Key"] for obj in response.get("Contents", [])}


def put_at(bucket: R2Bucket, key: str, last_modified: datetime) -> None:
    # moto keeps LastModified to the second, so back-to-back uploads tie.
    # Set it on moto's backend instead, to give each key a known time.
    put(bucket, key)
    backend = s3_backends[DEFAULT_ACCOUNT_ID]["aws"]
    backend.get_object(bucket.name, key).last_modified = last_modified


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name in R2_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


class TestFromEnv:
    def test_names_every_missing_variable(self, clean_env: pytest.MonkeyPatch) -> None:
        with pytest.raises(ValueError) as error:
            R2Bucket.from_env()

        for name in [
            "R2_ACCESS_KEY_ID",
            "R2_SECRET_ACCESS_KEY",
            "R2_ACCOUNT_ID",
            "R2_BUCKET",
        ]:
            assert name in str(error.value)

    def test_endpoint_url_replaces_account_id(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        clean_env.setenv("R2_ENDPOINT_URL", "http://localhost:9000")
        clean_env.setenv("R2_BUCKET", "pipeline-bucket")

        with pytest.raises(ValueError) as error:
            R2Bucket.from_env()

        assert "R2_ACCESS_KEY_ID" in str(error.value)
        assert "R2_SECRET_ACCESS_KEY" in str(error.value)
        assert "R2_ACCOUNT_ID" not in str(error.value)
        assert "R2_BUCKET" not in str(error.value)

    def test_repr_does_not_show_the_secret(self, clean_env: pytest.MonkeyPatch) -> None:
        clean_env.setenv("R2_ACCESS_KEY_ID", "fake-access-key-id")
        clean_env.setenv("R2_SECRET_ACCESS_KEY", "fake-secret-not-real")
        clean_env.setenv("R2_ACCOUNT_ID", "fake-account")
        clean_env.setenv("R2_BUCKET", "pipeline-bucket")

        bucket = R2Bucket.from_env()

        assert bucket.name == "pipeline-bucket"
        assert "fake-secret-not-real" not in repr(bucket)


class TestDownload:
    def test_replaces_an_old_local_file(self, bucket: R2Bucket, tmp_path: Path) -> None:
        put(bucket, "inputs/lookup.csv", b"new")
        path = tmp_path / "lookup.csv"
        path.write_bytes(b"old")

        assert bucket.download("inputs/lookup.csv", path) == path
        assert path.read_bytes() == b"new"

    def test_creates_parent_folders(self, bucket: R2Bucket, tmp_path: Path) -> None:
        put(bucket, "inputs/lookup.csv", b"new")
        path = tmp_path / "raw" / "inputs" / "lookup.csv"

        bucket.download("inputs/lookup.csv", path)

        assert path.read_bytes() == b"new"

    def test_missing_key_raises(self, bucket: R2Bucket, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="inputs/missing.csv"):
            bucket.download("inputs/missing.csv", tmp_path / "missing.csv")


class TestLatestKey:
    @pytest.fixture(autouse=True)
    def postcode_lookups(self, bucket: R2Bucket) -> None:
        # The newest CSV sorts first by name, and the newest key under the prefix
        # is not a CSV, so neither key order nor a missing filter can pass.
        put_at(bucket, f"{NSPL}_AUG_2025.csv", datetime(2025, 9, 1))
        put_at(bucket, f"{NSPL}_FEB_2025.csv", datetime(2025, 3, 1))
        put_at(bucket, f"{NSPL}_NOV_2025.zip", datetime(2025, 12, 1))
        put_at(bucket, "other/PostcodeDetails_NSPL_DEC_2025.csv", datetime(2026, 1, 1))

    def test_picks_the_newest_key(self, bucket: R2Bucket) -> None:
        assert bucket.latest_key(NSPL) == f"{NSPL}_NOV_2025.zip"

    def test_filters_by_suffix(self, bucket: R2Bucket) -> None:
        assert bucket.latest_key(NSPL, ".csv") == f"{NSPL}_AUG_2025.csv"

    def test_raises_when_no_key_matches(self, bucket: R2Bucket) -> None:
        with pytest.raises(FileNotFoundError):
            bucket.latest_key(NSPL, ".parquet")
        with pytest.raises(FileNotFoundError):
            bucket.latest_key("no-such-prefix/")


class TestUploadDirectory:
    @pytest.fixture
    def output(self, tmp_path: Path) -> Path:
        # manifest.json sorts before the other files, so it is not last by chance.
        (tmp_path / "manifest.json").write_bytes(b"{}")
        (tmp_path / "part-1.parquet").write_bytes(b"part 1")
        (tmp_path / "summary.csv").write_bytes(b"summary")
        (tmp_path / "tables").mkdir()
        (tmp_path / "tables" / "detail.parquet").write_bytes(b"detail")
        return tmp_path

    @pytest.fixture
    def uploaded(self, bucket: R2Bucket, monkeypatch: pytest.MonkeyPatch) -> list[str]:
        keys: list[str] = []
        upload_file = bucket.client.upload_file

        def recording_upload_file(
            filename: str, bucket_name: str, key: str, **kwargs: Any
        ) -> None:
            keys.append(key)
            upload_file(filename, bucket_name, key, **kwargs)

        monkeypatch.setattr(bucket.client, "upload_file", recording_upload_file)
        return keys

    def test_uploads_the_last_file_after_all_the_others(
        self, bucket: R2Bucket, output: Path, uploaded: list[str]
    ) -> None:
        bucket.upload_directory(output, "pipeline/2026-11-19", last="manifest.json")

        assert len(uploaded) == 4
        assert uploaded[-1] == "pipeline/2026-11-19/manifest.json"
        assert keys(bucket) == {
            "pipeline/2026-11-19/manifest.json",
            "pipeline/2026-11-19/part-1.parquet",
            "pipeline/2026-11-19/summary.csv",
            "pipeline/2026-11-19/tables/detail.parquet",
        }
        assert read(bucket, "pipeline/2026-11-19/tables/detail.parquet") == b"detail"

    def test_missing_last_file_uploads_nothing(
        self, bucket: R2Bucket, output: Path, uploaded: list[str]
    ) -> None:
        (output / "manifest.json").unlink()

        with pytest.raises(FileNotFoundError, match="manifest.json"):
            bucket.upload_directory(output, "pipeline", last="manifest.json")

        assert uploaded == []
