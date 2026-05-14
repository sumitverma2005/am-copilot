#!/usr/bin/env python3
"""Upload all 30 synthetic call files + gold-labels.json + manifest.json to S3.

Bucket: am-copilot-synthetic-{account}-{region}
Prefix: synthetic/

Usage:
    python scripts/upload_synthetic_to_s3.py
"""
import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

REGION = "us-east-1"
S3_PREFIX = "synthetic/"
LOCAL_DIR = Path(__file__).parents[1] / "data" / "synthetic"


def main() -> None:
    session = boto3.Session(
        profile_name=os.environ.get("AWS_PROFILE", "am-copilot-dev"),
        region_name=REGION,
    )
    sts = session.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    bucket = f"am-copilot-synthetic-{account_id}-{REGION}"

    s3 = session.client("s3")

    # Ensure bucket exists
    try:
        s3.head_bucket(Bucket=bucket)
        print(f"Bucket exists: {bucket}")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            print(f"Creating bucket: {bucket}")
            s3.create_bucket(Bucket=bucket)
        else:
            raise

    files = sorted(LOCAL_DIR.glob("*.json"))
    if not files:
        print(f"No JSON files found in {LOCAL_DIR}")
        sys.exit(1)

    uploaded = 0
    for path in files:
        key = f"{S3_PREFIX}{path.name}"
        s3.upload_file(str(path), bucket, key)
        print(f"  uploaded s3://{bucket}/{key}")
        uploaded += 1

    print(f"\nDone — {uploaded} files uploaded to s3://{bucket}/{S3_PREFIX}")


if __name__ == "__main__":
    try:
        main()
    except (BotoCoreError, ClientError) as e:
        print(f"AWS error: {e}", file=sys.stderr)
        sys.exit(1)
