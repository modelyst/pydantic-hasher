# pydasher

A small set of utility functions and mixins for deterministically hashing pydantic base-models.

## Basic Usage

The most useful function is the basic `hasher` function that takes in a BaseModel with standard datatypes on it and outputs a md5 hash of the contents. The field data used to generate the hash can be customized by marking fields that should be excluded from the hash in the `_hashexclude_` field.

```Python
from pydantic import BaseModel
from datetime import datetime
from pydasher import hasher


class User(BaseModel):
    user_id: int
    last_updated: datetime
    _hashexclude_ = {"last_updated"}


user_1 = User(user_id=1, last_updated=datetime(month=1, year=2021, day=1))
user_2 = User(user_id=2, last_updated=datetime(month=1, year=2021, day=1))
user_1_hash = hasher(user_1)
user_2_hash = hasher(user_2)
assert user_1_hash != user_2_hash

# Last updated can be changed without affecting the hash
user_1.last_updated = datetime(month=1, year=2021, day=2)
assert hasher(user_1) == user_1_hash

# if user_id is changed the hash is changed
user_1.user_id = 2
assert hasher(user_1) != user_1_hash
assert hasher(user_1) == hasher(user_2)
```

## Basic Mixin Use

We also expose a class mixin that provides useful methods directly to pydantic BaseModel instances.

```Python
from pydantic import BaseModel
from datetime import datetime
from pydasher import HashMixIn


class User(HashMixIn,BaseModel):
    user_id: int
    last_updated: datetime
    _hashexclude_ = {"last_updated"}


user_1 = User(user_id=1, last_updated=datetime(month=1, year=2021, day=1))
user_2 = User(user_id=2, last_updated=datetime(month=1, year=2021, day=1))
assert user_1.hash != user_2.hash

# Last updated can be changed without affecting the hash
old_hash = user_1.hash
user_1.last_updated = datetime(month=1, year=2021, day=2)
assert user_1.hash == old_hash

# if user_id is changed the hash is changed
user_1.user_id = 2
assert user_1.hash != old_hash
assert user_1.hash == user_2.hash
```
