from fizzbuzz import fizzbuzz


def test_first_five():
    assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_fifteen_is_fizzbuzz():
    assert fizzbuzz(15)[-1] == "FizzBuzz"


def test_length_matches_n():
    assert len(fizzbuzz(100)) == 100


def test_zero_gives_empty_list():
    assert fizzbuzz(0) == []


def test_all_items_are_strings():
    assert all(isinstance(x, str) for x in fizzbuzz(20))


def test_thirty():
    result = fizzbuzz(30)
    assert result[8] == "Fizz"   # 9
    assert result[9] == "Buzz"   # 10
    assert result[29] == "FizzBuzz"  # 30
