from temperature_converter import celsius_to_fahrenheit, fahrenheit_to_celsius


def test_freezing_point_to_fahrenheit():
    assert celsius_to_fahrenheit(0) == 32


def test_boiling_point_to_fahrenheit():
    assert celsius_to_fahrenheit(100) == 212


def test_negative_celsius():
    assert celsius_to_fahrenheit(-40) == -40


def test_decimal_celsius_is_rounded():
    assert celsius_to_fahrenheit(36.6) == 97.9


def test_fahrenheit_to_celsius():
    assert fahrenheit_to_celsius(212) == 100
    assert fahrenheit_to_celsius(32) == 0


def test_fahrenheit_to_celsius_is_rounded():
    assert fahrenheit_to_celsius(100) == 37.8
