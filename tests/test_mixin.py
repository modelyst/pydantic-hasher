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

from typing import List, Set

from pydantic import BaseModel

from pydasher.base import HashMixIn
from tests.examples import Dummy, NestedDummy


def test_basic_mixin():
    dummy = Dummy(key_1="1", key_2="2", key_3="3")
    assert isinstance(dummy, Dummy)
    assert dummy.dict() == {"key_1": "1", "key_2": "2", "key_3": 3.0}
    non_id_dict = dummy.dict()
    id_dict = dummy._id_dict()
    assert "key_3" in non_id_dict
    assert "key_3" not in id_dict
    assert dummy.hash == dummy.parse_obj(dummy.dict()).hash


def test_nested_mixin():
    dummy = Dummy(key_1="1", key_2="2", key_3="3")
    nested_dummy = NestedDummy(key_1="1", key_2=dummy, key_3="3")
    nested_dummy.dict()
    assert nested_dummy.hash == nested_dummy.parse_obj(nested_dummy.dict()).hash


class DummyList(HashMixIn, BaseModel):
    list_val: List[int]


class DummySet(HashMixIn, BaseModel):
    list_val: Set[int]


def test_hashability():
    class Dummy(HashMixIn, BaseModel):
        x: int = 1
        y: str = "a"
        z: str = "a"
        _hashinclude_ = {"x", "y"}

    obj_1 = Dummy()
    obj_2 = Dummy(x="2")
    obj_3 = Dummy(y="2")
    obj_4 = Dummy(z=1)
    obj_5 = Dummy(x=2)
    set_list = {obj_1, obj_2, obj_3, obj_4, obj_5}
    assert len(set_list) == 3
