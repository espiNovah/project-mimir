from conversation_history import add_message, start_conversation


def test_starts_with_system_message():
    history = start_conversation("You are a helpful tutor.")
    assert history == [{"role": "system", "content": "You are a helpful tutor."}]


def test_conversations_are_independent():
    a = start_conversation("You are a helpful tutor.")
    add_message(a, "user", "What is 2 + 2?")
    add_message(a, "assistant", "4")
    b = start_conversation("You are a pirate.")
    assert b == [{"role": "system", "content": "You are a pirate."}]
    assert len(a) == 3


def test_new_list_every_time():
    assert start_conversation("x") is not start_conversation("x")


def test_explicit_list_is_used():
    existing = []
    result = start_conversation("hi", existing)
    assert result is existing
    assert existing == [{"role": "system", "content": "hi"}]
