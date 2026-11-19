"""Shared fixtures: an R2 bucket backed by moto's in-memory S3."""

from __future__ import annotations

from collections.abc import Iterator

import boto3
import pytest
from moto import mock_aws

from tdc_python_utils.r2 import R2Bucket


@pytest.fixture
def bucket() -> Iterator[R2Bucket]:
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        yield R2Bucket(client=client, name="test-bucket")
