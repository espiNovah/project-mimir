def _normalize(tags: list[str]) -> set[str]:
    return {tag.lower() for tag in tags}


def common_tags(tags_a: list[str], tags_b: list[str]) -> list[str]:
    """Return the tags that appear in both lists, lower-cased, without repeats, sorted A to Z."""
    return sorted(_normalize(tags_a) & _normalize(tags_b))


def all_tags(tags_a: list[str], tags_b: list[str]) -> list[str]:
    """Return every tag from either list, lower-cased, without repeats, sorted A to Z."""
    return sorted(_normalize(tags_a) | _normalize(tags_b))
