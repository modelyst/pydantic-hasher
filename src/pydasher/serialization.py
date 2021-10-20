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

import json
from datetime import date, datetime, timedelta
from hashlib import md5
from typing import Any, Callable, Dict, Mapping, Sequence, Union
from uuid import UUID

from pydantic import BaseModel

from pydasher.datatypes import DefaultTypes
from pydasher.import_module import import_string

simple = (int, str, float, bool, type(None))
iterables = (list, set, tuple)

# Constant strings for encoding objects into jsonable dictionaries
HASH_EXCLUDE_FIELD = "_hashexclude_"
HASH_INCLUDE_FIELD = "_hashinclude_"
TYPE_NAME = "_type"
MODEL_TYPE_NAME = "_base_model_type"
VALUE_NAME = "_value"

JSONABLE_TYPE = Union[str, int, float, None, Mapping, Sequence]


def serialize(thing: Any, encoders: dict = {}, id_only: bool = True) -> JSONABLE_TYPE:
    """Serialize pydantic models to jsonable fields.

    Args:
        thing (Any): Python object to be serialized
        id_only (bool, optional): Only serialize the identifying information (excluding the fields in the _hashexclude_ field on pydantic models). Defaults to False.

    Raises:
        TypeError: Unknown built-in or custom type encountered that has not been accounted for

    Returns:
        [type]: [description]
    """
    # parse thing's metadata for deserialization and object type determination
    module, ptype = type(thing).__module__, type(thing).__name__
    derived_type = f"{module}.{ptype}"
    # Just return simple built in python objects as they have deterministic string forms
    if isinstance(thing, simple):
        return thing
    # Lists, tuples, and dicts are recursively iterated through to deal with nested models
    elif isinstance(thing, list):
        return [serialize(x, encoders, id_only=id_only) for x in thing]
    elif isinstance(thing, dict):
        assert all(
            [isinstance(k, str) for k in thing.keys()]
        ), f"Cannot serialize dictionaries with non string keys: {thing}"
        return {
            TYPE_NAME: DefaultTypes.DICT.value,
            VALUE_NAME: {
                k: serialize(v, encoders, id_only=id_only) for k, v in thing.items()
            },
        }
    elif isinstance(thing, tuple):
        return {
            TYPE_NAME: DefaultTypes.TUPLE.value,
            VALUE_NAME: [serialize(x, encoders, id_only=id_only) for x in thing],
        }
    # Sets need to be sorted to create a stable hash as they have no inherent order in python
    elif isinstance(thing, set):
        try:
            return {
                TYPE_NAME: DefaultTypes.SET.value,
                VALUE_NAME: [
                    serialize(x, encoders, id_only=id_only) for x in sorted(thing)
                ],
            }
        except TypeError as exc:
            raise ValueError(
                f"Cannot serialize set as elements cannot be sorted for deterministic hashing: {thing}"
            ) from exc
    elif isinstance(thing, BaseModel):
        # Exclude the fields set in the classes _hashexclude_ field to remove certain fields from affecting the hash
        exclude = getattr(thing, HASH_EXCLUDE_FIELD, set())
        include = getattr(thing, HASH_INCLUDE_FIELD, None)
        filter_func = lambda x: x not in exclude and (not include or x in include)
        return {
            TYPE_NAME: DefaultTypes.BASE_MODEL.value,
            MODEL_TYPE_NAME: derived_type,
            VALUE_NAME: {
                key: serialize(getattr(thing, key, id_only), encoders)
                for key in thing.__fields__
                if id_only and filter_func(key)
            },
        }
    elif isinstance(thing, datetime):
        return {TYPE_NAME: DefaultTypes.DATETIME.value, VALUE_NAME: thing.isoformat()}
    elif isinstance(thing, timedelta):
        return {
            TYPE_NAME: DefaultTypes.TIMEDELTA.value,
            VALUE_NAME: thing.total_seconds(),
        }
    elif isinstance(thing, UUID):
        return {TYPE_NAME: DefaultTypes.UUID.value, VALUE_NAME: str(thing)}
    elif type(thing) in encoders:
        return {TYPE_NAME: derived_type, VALUE_NAME: encoders[type(thing)](thing)}
    # Add new parsers here for any new datatypes
    # Make sure to add a relevant constructor to the constructors variable below for deserialization
    raise TypeError(f"Unknown type found when serializing:\n{thing}\n{type(thing)}")


def deserialize(serialized_thing, decoders: Dict[str, Callable[[Any], Any]] = {}):
    # if primitive return value unchanged
    if isinstance(serialized_thing, simple):
        return serialized_thing
    # lists can be just recursively unpacked
    elif isinstance(serialized_thing, list):
        return [deserialize(v, decoders=decoders) for v in serialized_thing]

    if not isinstance(serialized_thing, dict):
        raise ValueError(
            f"The serialized object should be dict and is {type(serialized_thing)}"
        )
    for key in (VALUE_NAME, TYPE_NAME):
        assert (
            key in serialized_thing
        ), f"Invalid serialized object, missing keys: {key}\n{serialized_thing}"
    value = serialized_thing[VALUE_NAME]
    type_ = serialized_thing[TYPE_NAME]
    if type_ == DefaultTypes.TUPLE:
        return tuple(deserialize(ele, decoders) for ele in value)
    elif type_ == DefaultTypes.SET:
        return {deserialize(ele, decoders) for ele in value}
    elif type_ == DefaultTypes.DICT:
        return {key: deserialize(val, decoders) for key, val in value.items()}
    elif type_ == DefaultTypes.TIMEDELTA:
        return timedelta(seconds=value)
    elif type_ == DefaultTypes.DATE:
        return date.fromisoformat(value)
    elif type_ == DefaultTypes.DATETIME:
        return datetime.fromisoformat(value)
    elif type_ == DefaultTypes.BASE_MODEL:
        model_string = serialized_thing.pop("_base_model_type")
        model_type = import_string(model_string)
        return model_type(
            **{key: deserialize(val, decoders=decoders) for key, val in value.items()}
        )
    raise TypeError(f"Found unknown type during deserialization:\n{value}\n{type_}")


def json_dumps(thing, default=None, encoders={}, id_only=True):
    return json.dumps(
        serialize(thing, encoders, id_only),
        ensure_ascii=False,
        sort_keys=True,
        indent=None,
        separators=(",", ":"),
    )


def json_loads(thing):
    return deserialize(json.loads(thing))


def hasher(thing, encoders={}) -> str:
    if isinstance(thing, BaseModel):
        base_encoders = thing.__config__.json_encoders
    else:
        base_encoders = {}
    base_encoders.update(encoders)
    return md5(json_dumps(thing, encoders=base_encoders).encode("utf-8")).hexdigest()
