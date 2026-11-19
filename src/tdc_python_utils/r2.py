"""Read and write files in a Cloudflare R2 bucket, for code that runs in data pipelines.

R2 has an S3-compatible API, so this module uses boto3. Importing it has no side
effects: it adds no log handler, and it does not load a ``.env`` file.
"""

from __future__ import annotations

import logging
import os
import posixpath
from dataclasses import dataclass
from pathlib import Path

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# 256 MiB parts keep multi-GB files well under the limit of 10,000 parts.
_TRANSFER_CONFIG = TransferConfig(
    multipart_threshold=256 * 1024 * 1024,
    multipart_chunksize=256 * 1024 * 1024,
    max_concurrency=8,
)

_NOT_FOUND_CODES = {"404", "NoSuchKey", "NotFound"}


@dataclass(frozen=True)
class R2Bucket:
    """A boto3 S3 client bound to one R2 bucket.

    Only the client and the bucket name are fields, so the secret key is never in
    a field that ``repr``, a log line or a Sentry event can show.

    - ``from_env()`` reads ``R2_ACCESS_KEY_ID``, ``R2_SECRET_ACCESS_KEY`` and
      ``R2_BUCKET``, and ``R2_ACCOUNT_ID`` unless ``R2_ENDPOINT_URL`` is set. One
      ``ValueError`` names every variable that is missing.
    - ``download(key, path)`` always downloads, creates parent folders, and
      replaces a local file at ``path``. It raises ``FileNotFoundError`` when the
      key does not exist.
    - ``latest_key(prefix, suffix)`` returns the newest key, by last-modified time,
      that starts with ``prefix`` and ends with ``suffix``. The prefix goes to R2
      unchanged, so it can end part-way through a file name. It raises
      ``FileNotFoundError`` when no key matches.
    - ``upload_directory(directory, prefix, last)`` uploads each file under
      ``directory`` to ``<prefix>/<path relative to directory>``. ``last`` is a
      relative path, such as ``"manifest.json"``: that file goes after all the
      others, so a reader never sees a new manifest beside old files.
    """

    client: BaseClient
    name: str

    @classmethod
    def from_env(cls) -> R2Bucket:
        required = ["R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET"]
        endpoint_url = os.getenv("R2_ENDPOINT_URL")
        if not endpoint_url:
            required.append("R2_ACCOUNT_ID")
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        client = boto3.client(
            "s3",
            endpoint_url=endpoint_url
            or f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
            aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
            region_name="auto",
            config=Config(retries={"max_attempts": 10, "mode": "adaptive"}),
        )
        return cls(client=client, name=os.environ["R2_BUCKET"])

    def download(self, key: str, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.client.download_file(
                self.name, key, str(path), Config=_TRANSFER_CONFIG
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in _NOT_FOUND_CODES:
                raise FileNotFoundError(f"No object at r2://{self.name}/{key}") from exc
            raise
        logger.info(f"Downloaded r2://{self.name}/{key} to {path}")
        return path

    def latest_key(self, prefix: str, suffix: str = "") -> str:
        paginator = self.client.get_paginator("list_objects_v2")
        objects = (
            obj
            for page in paginator.paginate(Bucket=self.name, Prefix=prefix)
            for obj in page.get("Contents", [])
            if obj["Key"].endswith(suffix)
        )
        newest = max(objects, key=lambda obj: obj["LastModified"], default=None)
        if newest is None:
            raise FileNotFoundError(
                f"No object in r2://{self.name}/{prefix}* ends with {suffix!r}"
            )
        return newest["Key"]

    def upload_directory(
        self, directory: Path, prefix: str, last: str | None = None
    ) -> None:
        if not directory.is_dir():
            raise NotADirectoryError(directory)
        files = {
            path.relative_to(directory).as_posix(): path
            for path in sorted(directory.rglob("*"))
            if path.is_file()
        }
        if last is not None:
            if last not in files:
                raise FileNotFoundError(f"{last} is not a file in {directory}")
            files[last] = files.pop(last)  # Re-inserting moves it to the end.

        for relative, path in files.items():
            key = posixpath.join(prefix, relative)
            self.client.upload_file(str(path), self.name, key, Config=_TRANSFER_CONFIG)
            logger.info(f"Uploaded {path} to r2://{self.name}/{key}")
