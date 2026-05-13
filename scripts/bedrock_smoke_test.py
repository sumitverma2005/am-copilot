"""
Smoke test: verify Bedrock connectivity via the cross-region inference profile.
Usage: python scripts/bedrock_smoke_test.py
"""
import json
import sys
import os

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

load_dotenv()

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
REGION = os.getenv("AWS_REGION", "us-east-1")
PROFILE = os.getenv("AWS_PROFILE", "am-copilot-dev")


def main() -> None:
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    client = session.client("bedrock-runtime")

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 32,
        "messages": [{"role": "user", "content": 'Say exactly: Bedrock is alive'}],
    }

    try:
        response = client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json",
        )
        body = json.loads(response["body"].read())
        text = body["content"][0]["text"].strip()
        print(text)
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        msg = exc.response["Error"]["Message"]
        print(f"AWS error [{code}]: {msg}", file=sys.stderr)
        if code == "AccessDeniedException":
            print(
                "Hint: Bedrock model access may not be approved yet. "
                "Request access in the AWS console under Bedrock → Model access.",
                file=sys.stderr,
            )
        sys.exit(1)
    except NoCredentialsError:
        print(
            f"No credentials found for profile '{PROFILE}'. "
            "Check ~/.aws/config or set AWS_PROFILE in .env.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
