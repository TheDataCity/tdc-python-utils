import os
from pathlib import Path

from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()


class AzureStorageDownloader:
    def __init__(self, container_name, connection_string):
        self.conn_str = os.environ.get(connection_string, default="")
        self.container_name = container_name
        self.container_client = ContainerClient.from_connection_string(
            self.conn_str, self.container_name
        )
            # try:
            #     self.container_client = ContainerClient.from_connection_string(
            #         self.conn_str, first_of_prev_month
            #     )
            # except Exception as e:
            #     raise e
        pass

    def get_latest_blob_name(
        self, prefix: str, name_contains: str = "", name_does_not_contain: str = "", extension: str = ""
    ) -> str:
        """
        Returns the name of the latest blob (by last_modified) within the container under the given prefix.

        Parameters:
            - prefix 
                Prefix/folder path to search within the container, e.g. "output/".
            - name_contains
                Optional substring that must be present in the blob name.
            - name_does_not_contain
                Optional substring that MUST NOT be present in the blob name.
            - extension
                Optional file extension filter, e.g. ".duckdb".

        Raises:
            - ResourceNotFoundError
                If the container or no matching blobs are found.
        """
        if not self.container_client.exists():
            print(f"The container '{self.container_name}' does not exist.")
            return ""
        latest = None
        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            name: str = blob.name  # type: ignore[attr-defined]
            if name_contains and name_contains not in name:
                continue
            if name_does_not_contain and name_does_not_contain in name:
                continue
            if extension and not name.endswith(extension):
                continue
            if latest is None or blob.last_modified > latest[1]:  # type: ignore[attr-defined]
                latest = (name, blob.last_modified)

        if latest is None:
            print(f"[WARNING]: No matching blobs found in '{self.container_name}' with prefix '{prefix}'. \
                  Available blobs: {[b["name"] for b in self.container_client.list_blobs()]}")
            return ""

        return latest[0]

    def download_file(
        self, target_blob, target_path, local_dir, local_filename=None, force=False
    ):
        """
        Download a named-file from the container.

        Parameters:
        - target_blob: name of the blob (file) to download
        - target_path: path to the blob in the given container
        - local_dir: local directory path to save output file
        - local_filename: Optional renaming of target file
        - force: (Default=False). Download the file even if a file with that name already exists locally.

        """
        # Ensure local directory exists
        os.makedirs(local_dir, exist_ok=True)

        # Connect to container
        blobs = [blob.name for blob in self.container_client.list_blobs()]

        if not blobs:
            print("No files found in Azure container.")
            exit(0)

        # Get blob properties to know the size
        blob_client = self.container_client.get_blob_client(
            os.path.join(target_path, target_blob) if target_path else target_blob
        )
        blob_props = blob_client.get_blob_properties()
        total_size = blob_props.size

        output_path = (
            local_dir / local_filename if local_filename else local_dir / target_blob
        )  # Use local_filename if given.

        # Download with progress bar
        # only download if path doesn't already exist
        if not Path.exists(output_path) or force:
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
                stream = blob_client.download_blob(max_concurrency=2)
                for chunk in stream.chunks():
                    f.write(chunk)
                    pbar.update(len(chunk))
            print("Download complete!")
        else:
            print(f"File already exists: {output_path}")
