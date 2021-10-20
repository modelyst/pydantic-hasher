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

from enum import Enum


class DefaultTypes(str, Enum):
    DICT = "dict"
    SET = "set"
    TUPLE = "tuple"
    DATETIME = "datetime"
    TIMEDELTA = "timedelta"
    DATE = "date"
    BASE_MODEL = "basemodel"
    UUID = "uuid"
    # TODO: Add encoders and decoders
    TIME = "time"
    ENUM = "enum"
    IPV4_ADDRESS = "IPv4Address"
    IPV4_NETWORK = "IPv4Network"
    IPV6_ADDRESS = "IPv6Address"
    IPV6_NETWORK = "IPv6Network"
    BYTES = "bytes"
    DECIMAL = "decimal"
    PATH = "path"
