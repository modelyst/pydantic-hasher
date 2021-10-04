#   Copyright 2021 Modelyst LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from datetime import date, datetime
from json import dumps, loads
from uuid import UUID

from hypothesis import given
from hypothesis import strategies as st
from pydantic import BaseModel

from pydasher.base import HashMixIn
from pydasher.serialization import get_id_dict, hasher

from .strategies import book_strat, json_strat


def serial_test(thing):
    hash_val = hasher(thing)
    assert isinstance(hash_val, str)
    new_thing = thing.parse_obj(thing.dict())
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
    assert dummy_1.dict() != dummy_2.dict()
    assert get_id_dict(dummy_1) == get_id_dict(dummy_2)
    assert hasher(dummy_1) != hasher(dummy_3)
    assert hasher(dummy_2) != hasher(dummy_3)
    assert type(dummy_4) != type(dummy_1)
    assert "ex_key" in get_id_dict(dummy_4)


class DummyClass2(HashMixIn, BaseModel):
    time: datetime
    id_val: UUID

    class Config:
        json_encoders = {
            UUID: lambda x: str(x),
            datetime: lambda x: x.isoformat(),
        }


class DummyClass3(DummyClass2):
    date: date

    class Config:
        json_encoders = {
            date: lambda x: x.isoformat(),
        }


@given(st.builds(DummyClass2))
def test_non_builtin_serialization_reverse(instance: DummyClass2):
    serial_test(instance)


@given(st.builds(DummyClass3))
def test_non_builtin_serialization_reverse_subclass(instance: DummyClass3):
    serial_test(instance)


@given(json_strat())
def test_raw_json(thing):
    thing_copy = loads(dumps(thing))
    assert hasher(thing_copy) == hasher(thing)
