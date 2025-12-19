from zipfile import ZipFile
from pathlib import Path
import polars as pl

def zip_to_polars(path: Path | str, file_format="csv", **kwargs) -> pl.DataFrame:
    """
    Docstring for zip_to_polars
    
    :param path: path to the source file
    :type path: Path | str
    :param file_format: csv or parquet
    :param kwargs: keyword arguments for polars
    :return: Polars dataframe of the source file
    :rtype: DataFrame
    """
    with ZipFile(path) as zf:
        name_list = zf.namelist()

        if len(name_list) == 1:
            # There is only one file, just load and return it
            print(f"Loading {name_list[0]} from zip.")

            if file_format == "csv":
                df = pl.read_csv(zf.open(name_list[0]), **kwargs)

            # elif file_format == "json":
            #     df = pl.read_json(zf.open(name_list[0]))

            elif file_format == "parquet":
                df = pl.read_parquet(zf.open(name_list[0]), **kwargs)

            else:
                print(f"Format: {file_format} not supported.")
                df = pl.DataFrame()

            return df

        else:
            print("More than one file in this zip.")
            return pl.DataFrame()