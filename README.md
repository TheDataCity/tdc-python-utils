# tdc-python-utils

A utility package for python users at The Data City.

The aim is to reduce code repetition, increase maintanability of our codebase, and cascade continual improvements into all python-based projects.

Written and maintained by [Luke Strange](https://thedatacity.com/about-us/meet-the-team/luke-strange/).

## Set-up

1. Clone the repository

2. [Install uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already.

3. Run `uv sync`

## Publishing a release

After making your changes:

0. Run `uv run ruff check` and fix any errors. Commit changes to GitHub

1. Set the new version number in `pyproject.toml`

2. Ensure `twine` can see your environment variables:

    ```sh
    set -a        # turn on auto-export
    source .env  # load variables AND export them
    set +a        # turn auto-export back off
    ```

3. Make the build: `uv build`

4. Publish the release:

    ```sh
    uv run twine upload --repository testpypi dist/tdc_python_utils-X.Y.Z*
    ```

    where `X.Y.Z` is the version number to publish.
