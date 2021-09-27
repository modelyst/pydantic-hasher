from typing import TYPE_CHECKING, Any, ClassVar, Set
from uuid import UUID

from .serialization import JSONABLE_TYPE, from_dict, hasher, to_dict

if TYPE_CHECKING:
    from pydantic import BaseModel


class HashMixIn:
    """A mixin for pydantic BaseModels to add a deterministic hash."""

    _hashexclude_: ClassVar[Set[str]] = set()

    def __eq__(self, other: Any) -> bool:
        """
        Maybe the below should be preferred? Try it out, sometime!
        return type(self) == type(other) and vars(self) == vars(other)
        """
        if type(other) == type(self):
            return self.hex == other.hex
        else:
            err = f"Equality type error \n{self} \n({type(self)}) \n\n{other} \n({type(other)})"
            raise ValueError(err)

    def __hash__(self) -> int:
        return int(self.hex, 16)

    @property
    def hash(self) -> str:
        return self.hex

    @property
    def hex(self) -> str:
        return hasher(self)

    @property
    def uuid(self) -> str:
        return str(UUID(self.hash).hex)

    def to_dict(self, id_only: bool = False) -> JSONABLE_TYPE:
        return to_dict(self, id_only)

    @staticmethod
    def from_dict(input_dict: dict) -> "BaseModel":
        return from_dict(input_dict)
