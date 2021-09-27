from datetime import date, datetime
from uuid import UUID, uuid4

from hypothesis import given, strategies as st
from pydantic import BaseModel
from pydasher import from_dict, hasher, to_dict

from .strategies import book_strat


def serial_test(thing):
    hash_val = hasher(thing)
    assert isinstance(hash_val, str)
    new_thing = from_dict(to_dict(thing))
    assert hasher(new_thing) == hash_val


@given(book_strat)
def test_basic_hashing(thing):
    serial_test(thing)


class DummyClass(BaseModel):
    key_1: str
    key_2: int
    key_3 = "test"
    ex_key: str

    _hashexclude_ = {"ex_key"}


class DummyClassNoExclude(BaseModel):
    key_1: str
    key_2: int
    ex_key: str


def test_exclude():
    dummy_1 = DummyClass(key_1="1", key_2=2, ex_key="1")
    dummy_2 = DummyClass(key_1="1", key_2=2, ex_key="2")
    dummy_3 = DummyClass(key_1="1", key_2=0, ex_key="2")
    dummy_4 = DummyClassNoExclude(key_1="1", key_2=0, ex_key="2")

    assert hasher(dummy_1) == hasher(dummy_2)
    assert to_dict(dummy_1) != to_dict(dummy_2)
    assert to_dict(dummy_1, id_only=True) == to_dict(dummy_2, id_only=True)
    assert hasher(dummy_1) != hasher(dummy_3)
    assert hasher(dummy_2) != hasher(dummy_3)
    assert type(dummy_4) != type(dummy_1)
    assert "ex_key" in to_dict(dummy_4, id_only=True)


class DummyClass2(BaseModel):
    time: datetime
    date: date
    id_val: UUID


def test_non_builtin_serialization():
    value = uuid4()
    assert value == from_dict(to_dict(value, False))
    value = datetime.now()
    assert value == from_dict(to_dict(value, False))
    value = datetime.now().date()
    assert value == from_dict(to_dict(value, False))
    value = DummyClass2(time=datetime.now(), id_val=uuid4(), date=datetime.now().date())
    assert value == from_dict(to_dict(value, False))


@given(st.builds(DummyClass2))
def test_non_builtin_serialization_reverse(instance: DummyClass2):
    serial_test(instance)
