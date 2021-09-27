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

from typing import Any, ClassVar, Optional, Set
from uuid import UUID

from pydasher.serialization import JSONABLE_TYPE, get_id_dict, hasher


class HashMixIn:
    """A mixin for pydantic BaseModels to add a deterministic hash."""

    _hashexclude_: ClassVar[Set[str]] = set()
    _hashinclude_: ClassVar[Optional[Set[str]]] = None

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
    def uuid(self) -> UUID:
        return UUID(hex=self.hex)

    def _id_dict(self) -> JSONABLE_TYPE:
        config = getattr(self, "__config__", object())
        encoders = getattr(config, "json_encoders", {})
        return get_id_dict(self, encoders)
