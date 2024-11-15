
import pytest
from codes.implements.my_function import capital_case, find_max_element

def test_capital_case():
    assert capital_case("hello") == "Hello"
    assert capital_case("world") == "World"

def test_find_max_element():
    assert find_max_element([1, 2, 3, 4, 5]) == 5
    assert find_max_element([10, 20, 30]) == 30
