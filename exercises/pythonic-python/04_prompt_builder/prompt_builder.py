def build_prompt(*parts: str, sep: str = "\n\n", **variables: str) -> str:
    """Join the non-empty parts with sep, then fill in {placeholders} from variables.

    build_prompt("Hello {name}.", "Bye.", name="Ada") == "Hello Ada.\n\nBye."
    """
    raise NotImplementedError("Write this function")


def call_with_defaults(func, *args, **kwargs):
    """Call func with args and kwargs, adding temperature=0.0 unless the caller passed one."""
    raise NotImplementedError("Write this function")
