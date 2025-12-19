from azure.storage.blob import ContainerClient
import os
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

class AzureStorageDownloader:
    def __init__(self, container_name:str, connection_string:str):
        """
        :param container_name: The name of the container on Azure storage. e.g. "2025-12-01" or "creditsafe"
        :param connection_string: The name of your connection string envirnoment variable. Use the azure storage explorer to find this.
        """
        self.conn_str = os.environ.get(connection_string)
        self.container_name = container_name
        pass

    def download_file(self, target_blob:str, target_path:str, local_dir:str) -> None:
        """
        Download a single file from Azure blob storage.
        
        :param target_blob: The blob you want to download (the name of the file including the extension)
        :type target_blob: str
        :param target_path: Description The path to the blob you want to download
        :type target_path: str
        :param local_dir: Description The local directory to save the file to
        :type local_dir: str
        """
        # Ensure local directory exists
        os.makedirs(local_dir, exist_ok=True)

        # Connect to container
        container = ContainerClient.from_connection_string(self.conn_str, self.container_name)
        
        blobs = [blob.name for blob in container.list_blobs()]

        if not blobs:
            print("No files found in Azure container.")
            exit(0)

        # Get blob properties to know the size
        blob_client = container.get_blob_client(os.path.join(target_path, target_blob))
        blob_props = blob_client.get_blob_properties()
        total_size = blob_props.size

        # Download with progress bar
        with open(local_dir / target_blob, "wb") as f, tqdm(total=total_size, unit='B', unit_scale=True, desc=target_blob) as pbar:
            stream = blob_client.download_blob(max_concurrency=2)
            for chunk in stream.chunks():
                f.write(chunk)
                pbar.update(len(chunk))

        print("Download complete!")
