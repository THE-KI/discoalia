import json
import os
from commands import m10randomizer, discoaliadev

from nacl.signing import VerifyKey

APPLICATION_PUBLIC_KEY = os.getenv("APPLICATION_PUBLIC_KEY")

verify_key = VerifyKey(bytes.fromhex(APPLICATION_PUBLIC_KEY))


def verify(signature: str, timestamp: str, body: str) -> bool:
    try:
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
    except Exception as e:
        print(f"failed to verify request: {e}")
        return False

    return True


def callback(event: dict, context: dict):
    # API Gateway has weird case conversion, so we need to make them lowercase.
    # See https://github.com/aws/aws-sam-cli/issues/1860
    headers: dict = {k.lower(): v for k, v in event["headers"].items()}
    rawBody: str = event["body"]

    # validate request
    signature = headers.get("x-signature-ed25519")
    timestamp = headers.get("x-signature-timestamp")
    if not verify(signature, timestamp, rawBody):
        return {
            "cookies": [],
            "isBase64Encoded": False,
            "statusCode": 401,
            "headers": {},
            "body": "",
        }

    req: dict = json.loads(rawBody)
    if req["type"] == 1:  # InteractionType.Ping
        return {"type": 1}  # InteractionResponseType.Pong
    elif req["type"] == 2:  # InteractionType.ApplicationCommand
        cmd = req["data"]["name"]

        if "discoaliadev" in cmd:
            print(req)
            executor_name = req["member"]["nick"] or req["member"]["user"]["username"]
            print(executor_name)
            text = discoaliadev.exec(executor_name)

        if "m10randomizer" in cmd:
            executor_name = req["member"]["nick"] or req["member"]["user"]["username"]
            text = m10randomizer.exec(executor_name)

        return {
            "type": 4,  # InteractionResponseType.ChannelMessageWithSource
            "data": {"content": text},
        }
