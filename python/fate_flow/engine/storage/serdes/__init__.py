#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#


def get_serdes_by_type(serdes_type: int):
    if serdes_type == 0:
        from ._unrestricted_serdes import get_unrestricted_serdes

        return get_unrestricted_serdes()
    elif serdes_type == 1:
        from ._integer_serdes import get_integer_serdes

        return get_integer_serdes()
    else:
        raise ValueError(f"serdes type `{serdes_type}` not supported")
