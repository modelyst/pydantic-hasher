import json
from datetime import date, datetime
from importlib import import_module
from typing import Any, Mapping, Sequence, Union
from uuid import UUID
from hashlib import md5
from pydantic.types import SecretStr
from pydantic import BaseModel

simple = (int, str, float, bool)
iterables = (list, set, tuple)

HASH_EXCLUDE_FIELD = "_hashexclude_"

JSONABLE_TYPE = Union[str, int, float, None, Mapping, Sequence]


def to_dict(thing: Any, id_only: bool = False) -> JSONABLE_TYPE:
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
    _is_base_model = isinstance(thing, BaseModel)
    metadata = {"_pytype": f"{module}.{ptype}", "_is_base_model": _is_base_model}

    if module == "builtins":
        # Just return simple built in python objects as they have deterministic string forms
        if isinstance(thing, simple) or thing is None:
            return thing
        # Lists, tuples, and dicts are recursively iterated through to deal with nested models
        elif isinstance(thing, (list, tuple)):
            return {**metadata, "_value": [to_dict(x, id_only) for x in thing]}
        elif isinstance(thing, dict):
            assert all([isinstance(k, str) for k in thing.keys()]), thing
            return {k: to_dict(v, id_only) for k, v in thing.items()}
        # Sets need to be sorted to create a stable hash as they have no inherent order in python
        elif isinstance(thing, set):
            return {
                **metadata,
                "_value": [to_dict(x, id_only) for x in sorted(thing)],
            }
        raise TypeError(
            thing,
            f"Unknown builtin python type {ptype}, haven't implemented a parser: {thing}",
        )
    elif isinstance(thing, BaseModel):
        # Exclude the fields set in the classes _hashexclude_ field to remove certain fields from affecting the hash
        exclude = getattr(thing, HASH_EXCLUDE_FIELD, set()) if id_only else set()
        return {
            **metadata,
            **{
                key: to_dict(value, id_only)
                for key, value in thing
                if key not in exclude
            },
        }
    # Ad hoc parsers for very common datatypes
    elif isinstance(thing, UUID):
        return {**metadata, "_value": str(thing)}
    elif isinstance(thing, (datetime, date)):
        return {**metadata, "_value": thing.isoformat()}
    elif isinstance(thing, SecretStr):
        return {**metadata, "_value": thing.get_secret_value()}
    # Add new parsers here for any new datatypes
    # Make sure to add a relevant constructor to the constructors variable below for deserialization
    raise TypeError(f"Unknown type found when serializing:\n{thing}\n{type(thing)}")


constructors = {
    "uuid.UUID": lambda x: UUID(x),
    "datetime.datetime": lambda x: datetime.fromisoformat(x),
    "datetime.date": lambda x: date.fromisoformat(x),
}


def from_dict(thing: JSONABLE_TYPE) -> Any:
    """Create a python/pydantic models from a JSON serializable structure."""
    if isinstance(thing, dict):
        # grab the metadata to differentiate between dicts and dictified python objects
        ptype = thing.pop("_pytype", "")
        is_base_model = thing.pop("_is_base_model", False)

        # Import the constructor and assemble the object
        if is_base_model:
            mod, cname = ".".join(ptype.split(".")[:-1]), ptype.split(".")[-1]
            constructor = getattr(import_module(mod), cname)
            return constructor(
                **{
                    k: from_dict(v)
                    for k, v in thing.items()
                    if k in constructor.__fields__
                }
            )
        # Use custom constructors for the adhoc types
        elif ptype in constructors:
            return constructors[ptype](thing.get("_value"))
        # Recursively parse all iterables
        elif ptype in ("builtins/tuple", "builtins.tuple"):
            return tuple([from_dict(xx) for xx in thing["_value"]])  # data-level tuple
        elif ptype in ("builtins/set", "builtins.set"):
            return {from_dict(xx) for xx in thing["_value"]}  # data-level tuple
        elif ptype == "builtins.list":
            return [from_dict(xx) for xx in thing["_value"]]  # data-level tuple
        else:
            assert (
                "_ptype" not in thing
            ), f"I found _ptype on a what is assumed to be a base dictionary rather than a python object. This was assumed to never happen unless _ptype is a true key on your dict.\n {thing}"
            return {k: from_dict(v) for k, v in thing.items()}  # data-level dict
    # Simple objects can be recursed or returned
    elif isinstance(thing, (int, float, list, type(None), str)):
        if isinstance(thing, list):
            return [from_dict(xx) for xx in thing]
        else:
            return thing
    else:
        raise TypeError(
            thing,
            f"Invalid type found when traversing the serialized object:\n{type(thing)}\n{thing}",
        )


def json_dumps(thing, default=None, id_only: bool = False):
    return json.dumps(
        to_dict(thing, id_only),
        ensure_ascii=False,
        sort_keys=True,
        indent=None,
        separators=(",", ":"),
    )


def hasher(thing) -> str:
    return md5(json_dumps(thing, id_only=True).encode("utf-8")).hexdigest()
