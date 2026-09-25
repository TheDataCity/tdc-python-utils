import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from loguru import logger
from tqdm import tqdm

logger.add(f"logs/DailyUpdates_UK/{Path(__file__).stem}.log", retention="30 days")

load_dotenv()


class R2StorageDownloader:
    def __init__(self, container_name: str):
        key = os.environ.get("R2_ACCESS_KEY_ID", "")
        secret = os.environ.get("R2_SECRET_ACCESS_KEY", "")
        account = os.environ.get("R2_ACCOUNT_ID", "")
        bucket = os.environ.get("R2_BUCKET", "")
        if not key or not secret or not account or not bucket:
            raise KeyError(
                "Set R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ACCOUNT_ID, R2_BUCKET"
            )
        endpoint = os.environ.get(
            "R2_ENDPOINT_URL", f"https://{account}.r2.cloudflarestorage.com"
        )
        self.container_name = container_name.strip("/")
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=key,
            aws_secret_access_key=secret,
            region_name=os.environ.get("R2_REGION", "auto"),
        )
        self.logger = logger

    def _key(self, *parts: str) -> str:
        cleaned = [self.container_name]
        for part in parts:
            if part:
                cleaned.append(str(part).strip("/"))
        return "/".join(cleaned)

    def list_objects(self, prefix: str = ""):
        """Yield (relative_name, last_modified) under the container prefix."""
        full_prefix = self._key(prefix) if prefix else self.container_name + "/"
        # Also allow listing container root
        if not prefix:
            full_prefix = self.container_name + "/"
        token = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": full_prefix}
            if token:
                kwargs["ContinuationToken"] = token
            resp = self.client.list_objects_v2(**kwargs)
            for obj in resp.get("Contents") or []:
                name = obj["Key"][len(self.container_name) + 1 :]
                if name:
                    yield name, obj["LastModified"]
            if not resp.get("IsTruncated"):
                break
            token = resp.get("NextContinuationToken")

    def get_latest_blob_name(
        self,
        prefix: str,
        name_contains: str = "",
        name_does_not_contain: str = "",
        extension: str = "",
    ) -> str:
        """
        Returns the object key relative to the container (by LastModified)
        under the given prefix.
        """
        full_prefix = self._key(prefix)
        latest = None
        token = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": full_prefix}
            if token:
                kwargs["ContinuationToken"] = token
            resp = self.client.list_objects_v2(**kwargs)
            for obj in resp.get("Contents") or []:
                name = obj["Key"][len(self.container_name) + 1 :]
                if name_contains and name_contains not in name:
                    continue
                if name_does_not_contain and name_does_not_contain in name:
                    continue
                if extension and not name.endswith(extension):
                    continue
                lm = obj["LastModified"]
                if latest is None or lm > latest[1]:
                    latest = (name, lm)
            if not resp.get("IsTruncated"):
                break
            token = resp.get("NextContinuationToken")

        if latest is None:
            logger.warning(
                f"No matching objects found in '{self.container_name}' with prefix '{prefix}'"
            )
            return ""

        return latest[0]

    def download_file(
        self, target_blob, target_path, local_dir, local_filename=None, force=False
    ):
        """
        Download a named object from the container prefix.

        Parameters:
        - target_blob: name of the object (file) to download
        - target_path: path within the container prefix
        - local_dir: local directory path to save output file
        - local_filename: Optional renaming of target file
        - force: (Default=False). Download even if a local file already exists.
        """
        os.makedirs(local_dir, exist_ok=True)
        key = self._key(target_path, target_blob)
        output_path = (
            Path(local_dir) / local_filename
            if local_filename
            else Path(local_dir) / target_blob
        )

        if Path.exists(output_path) and not force:
            logger.info(f"File already exists: {output_path}")
            return

        try:
            head = self.client.head_object(Bucket=self.bucket, Key=key)
        except ClientError as exc:
            logger.exception("Object not found on R2.")
            raise FileNotFoundError(key) from exc

        total_size = int(head["ContentLength"])
        transferred = {"n": 0}
        with (
            open(output_path, "wb") as f,
            tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=target_blob,
                mininterval=1,
            ) as pbar,
        ):

            def _cb(bytes_transferred: int) -> None:
                pbar.update(bytes_transferred - transferred["n"])
                transferred["n"] = bytes_transferred

            self.client.download_fileobj(self.bucket, key, f, Callback=_cb)
        logger.info("Download complete!")


# Back-compat alias for older imports / docs.
AzureStorageDownloader = R2StorageDownloader
