"""Thin SQS wrapper — keeps webhook.py testable without an AWS connection.

Environment variables required:
    EVALUATION_QUEUE_URL — SQS queue URL
    AWS_REGION           — e.g. us-east-1 (boto3 default region)
"""
from __future__ import annotations

import json
import os

import boto3


def enqueue(call_id: str, normalized_call: dict) -> str:
    """Push a normalized call to the evaluation SQS queue.

    Returns the SQS MessageId.
    """
    queue_url = os.environ["EVALUATION_QUEUE_URL"]
    sqs = boto3.client("sqs", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    body = json.dumps({"call_id": call_id, "normalized_call": normalized_call})
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=body)
    return response["MessageId"]
