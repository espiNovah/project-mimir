import json
import re

# ``` or ```json, then (lazily) everything up to the next ```.
FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def parse_json_reply(reply: str):
    """Parse JSON from a model reply, unwrapping the first ```/```json fence if there is one.

    Invalid JSON raises json.JSONDecodeError.
    """
    m = FENCE_RE.search(reply)
    body = m.group(1) if m else reply.strip()
    return json.loads(body)
