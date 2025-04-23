from src.utils import singleton


@singleton
class TestClass:
    def __init__(self):
        self.value = None


def test_singleton_returns_same_instance():
    instance1 = TestClass()
    instance2 = TestClass()

    assert instance1 is instance2


def test_singleton_maintains_state():
    instance1 = TestClass()
    instance1.value = "test"

    instance2 = TestClass()
    assert instance2.value == "test"


def test_singleton_works_with_multiple_calls():
    instance1 = TestClass()
    instance2 = TestClass()
    instance3 = TestClass()

    assert instance1 is instance2
    assert instance2 is instance3
