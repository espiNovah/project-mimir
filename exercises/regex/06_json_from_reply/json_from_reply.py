import json
import re


def parse_json_reply(reply: str):
    """Parse JSON from a model reply, unwrapping the first ```/```json fence if there is one.

    Invalid JSON raises json.JSONDecodeError.
    """
    raise NotImplementedError("Write this function")
