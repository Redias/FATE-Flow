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
from playhouse.pool import PostgresqlDatabase

from fate_flow.utils.password_utils import decrypt_database_config


def get_database_connection(config, decrypt_key):
    database_config = config.copy()
    db_name = database_config.pop("name")
    decrypt_database_config(database_config, decrypt_key=decrypt_key)
    return PostgresqlDatabase(db_name, **database_config)

