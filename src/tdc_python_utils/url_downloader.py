import io
from pathlib import Path

import requests
from tqdm import tqdm

from tdc_python_utils.colours import highlight_text

def download_zipfile_from_url(url, save_to: str | Path):
    if Path(save_to).exists():
        print(f"{save_to} already exists. Skipping download")
        return None

    print(highlight_text("Starting ZIP download...", "ZIP", "cyan"))
    buffer = None
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024
        buffer = io.BytesIO()

        with tqdm(
            total=total_size, unit="iB", unit_scale=True, desc="Downloading ZIP"
        ) as bar:
            for data in response.iter_content(block_size):
                buffer.write(data)
                bar.update(len(data))

    buffer.seek(0)
    with open(save_to, "wb") as f:
        f.write(buffer.getvalue())

    print(highlight_text(f"ZIP saved to {save_to}", str(save_to), "green"))
    return save_to
