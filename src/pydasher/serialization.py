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
from hashlib import md5
from typing import Any, Mapping, Sequence, Union

from pydantic import BaseModel

simple = (int, str, float, bool)
iterables = (list, set, tuple)

HASH_EXCLUDE_FIELD = "_hashexclude_"
HASH_INCLUDE_FIELD = "_hashinclude_"

JSONABLE_TYPE = Union[str, int, float, None, Mapping, Sequence]


def get_id_dict(thing: Any, encoders: dict = {}) -> JSONABLE_TYPE:
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
    metadata = {"_pytype": f"{module}.{ptype}"}

    if module == "builtins":
        # Just return simple built in python objects as they have deterministic string forms
        if isinstance(thing, simple) or thing is None:
            return thing
        # Lists, tuples, and dicts are recursively iterated through to deal with nested models
        elif isinstance(thing, (list, tuple)):
            return {**metadata, "_value": [get_id_dict(x, encoders) for x in thing]}
        elif isinstance(thing, dict):
            assert all([isinstance(k, str) for k in thing.keys()]), thing
            return {k: get_id_dict(v, encoders) for k, v in thing.items()}
        # Sets need to be sorted to create a stable hash as they have no inherent order in python
        elif isinstance(thing, set):
            return {
                **metadata,
                "_value": [get_id_dict(x, encoders) for x in sorted(thing)],
            }
        raise TypeError(
            thing,
            f"Unknown builtin python type {ptype}, haven't implemented a parser: {thing}",
        )
    elif isinstance(thing, BaseModel):
        # Exclude the fields set in the classes _hashexclude_ field to remove certain fields from affecting the hash
        exclude = getattr(thing, HASH_EXCLUDE_FIELD, set())
        include = getattr(thing, HASH_INCLUDE_FIELD, None)
        filter_func = lambda x: x not in exclude and (not include or x in include)
        return {
            **metadata,
            **{
                key: get_id_dict(value, encoders)
                for key, value in thing
                if filter_func(key)
            },
        }
    elif type(thing) in encoders:
        return encoders[type(thing)](thing)
    # Add new parsers here for any new datatypes
    # Make sure to add a relevant constructor to the constructors variable below for deserialization
    raise TypeError(f"Unknown type found when serializing:\n{thing}\n{type(thing)}")


def json_dumps(thing, default=None, encoders={}):
    return json.dumps(
        get_id_dict(thing, encoders),
        ensure_ascii=False,
        sort_keys=True,
        indent=None,
        separators=(",", ":"),
    )


def hasher(thing, encoders={}) -> str:
    if isinstance(thing, BaseModel):
        base_encoders = thing.__config__.json_encoders
    else:
        base_encoders = {}
    base_encoders.update(encoders)
    return md5(json_dumps(thing, encoders=base_encoders).encode("utf-8")).hexdigest()
