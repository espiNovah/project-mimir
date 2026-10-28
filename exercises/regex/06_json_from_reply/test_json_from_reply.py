import json

import pytest

from json_from_reply import parse_json_reply

FENCE = "`" * 3


def test_plain_json():
    assert parse_json_reply('{"label": "billing"}') == {"label": "billing"}


def test_plain_json_with_whitespace():
    assert parse_json_reply('\n  [1, 2, 3]  \n') == [1, 2, 3]


def test_fenced_with_language_tag():
    reply = f'Sure! Here is the data:\n\n{FENCE}json\n{{"label": "billing", "confidence": 0.9}}\n{FENCE}\n'
    assert parse_json_reply(reply) == {"label": "billing", "confidence": 0.9}


def test_fenced_without_language_tag():
    reply = f'{FENCE}\n{{"ok": true}}\n{FENCE}'
    assert parse_json_reply(reply) == {"ok": True}


def test_multiline_json():
    reply = f'{FENCE}json\n{{\n  "label": "bug",\n  "tags": ["login", "mobile"]\n}}\n{FENCE}'
    assert parse_json_reply(reply) == {"label": "bug", "tags": ["login", "mobile"]}


def test_first_fence_wins():
    reply = f'{FENCE}json\n{{"n": 1}}\n{FENCE}\nand another:\n{FENCE}json\n{{"n": 2}}\n{FENCE}'
    assert parse_json_reply(reply) == {"n": 1}


def test_invalid_json_raises():
    with pytest.raises(json.JSONDecodeError):
        parse_json_reply("I couldn't find any data, sorry.")
