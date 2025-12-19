from pathlib import Path

ROOT = Path.cwd()
RAW_DATA = ROOT / "raw_data"
PROCESSED_DATA = ROOT / "processed_data"

def setup_paths(paths_to_make:list[str]) -> None:
    """
    Create directories provided in paths_to_make in the current working directory
    
    :param paths_to_make: List of strings of paths to make
    :type paths_to_make: list[str]
    """
    full_paths = [ROOT / path for path in paths_to_make]

    for path in full_paths:
        path.mkdir(exist_ok=True, parents=True)
    
    print("Made all paths.")
