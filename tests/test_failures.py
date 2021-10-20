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

import pytest

from pydasher.datatypes import DefaultTypes
from pydasher.serialization import MODEL_TYPE_NAME, TYPE_NAME, VALUE_NAME, deserialize


def test_unknown_import():
    with pytest.raises(ModuleNotFoundError):
        deserialize(
            {
                TYPE_NAME: DefaultTypes.BASE_MODEL,
                MODEL_TYPE_NAME: "unknown.unknown",
                VALUE_NAME: {},
            }
        )


def test_invalid_import():
    with pytest.raises(ImportError):
        deserialize(
            {
                TYPE_NAME: DefaultTypes.BASE_MODEL,
                MODEL_TYPE_NAME: "unknown",
                VALUE_NAME: {},
            }
        )


def test_missing_key():
    with pytest.raises(AssertionError):
        deserialize(
            {
                TYPE_NAME: DefaultTypes.BASE_MODEL,
                MODEL_TYPE_NAME: "unknown",
            }
        )
