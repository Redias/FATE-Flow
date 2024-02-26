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
import json
import logging
import os
import traceback

import click

from fate_flow.entity.spec.dag import PreTaskConfigSpec, TaskConfigSpec, IOMeta
from fate_flow.hub.flow_hub import FlowHub

logger = logging.getLogger(__name__)


@click.group()
def component():
    """
    Manipulate components: execute, list, generate describe file
    """


@component.command()
@click.option("--config", required=False, type=click.File(), help="config path")
@click.option("--env-name", required=True, type=str, help="env name for config", default="CONFIG")
@click.option("--wraps-module", required=False, type=str, help="component run wraps module")
def entrypoint(config, env_name, wraps_module):
    # parse config
    configs = {}
    load_config_from_env(configs, env_name)
    load_config_from_file(configs, config)
    task_config = PreTaskConfigSpec.parse_obj(configs)
    task_config.conf.logger.install()
    logger = logging.getLogger(__name__)
    logger.debug("logger installed")
    logger.debug(f"task config: {task_config}")
    FlowHub.load_components_wraps(config=task_config, module_name=wraps_module).run()


@component.command()
@click.option("--config", required=False, type=click.File(), help="config path")
@click.option("--env-name", required=False, type=str, help="env name for config")
@click.option("--wraps-module", required=False, type=str, help="component run wraps module")
def cleanup(config, env_name, wraps_module=None):
    configs = {}
    load_config_from_env(configs, env_name)
    load_config_from_file(configs, config)
    task_config = PreTaskConfigSpec.parse_obj(configs)
    task_config.conf.logger.install()
    logger = logging.getLogger(__name__)
    logger.debug("logger installed")
    logger.debug(f"task config: {task_config}")
    FlowHub.load_components_wraps(config=task_config, module_name=wraps_module).cleanup()


@component.command()
@click.option("--config", required=False, type=click.File(), help="config path")
@click.option("--env-name", required=False, type=str, help="env name for config")
@click.option(
    "--execution-final-meta-path",
    type=click.Path(exists=False, dir_okay=False, writable=True, resolve_path=True),
    default=os.path.join(os.getcwd(), "execution_final_meta.json"),
    show_default=True,
    help="path for execution meta generated by component when execution finished",
)
def execute(config, env_name, execution_final_meta_path):
    # parse config
    configs = {}
    load_config_from_env(configs, env_name)
    load_config_from_file(configs, config)
    task_config = TaskConfigSpec.parse_obj(configs)
    task_config.conf.logger.install()
    logger = logging.getLogger(__name__)
    logger.debug("logger installed")
    logger.debug(f"task config: {task_config}")
    os.makedirs(os.path.dirname(execution_final_meta_path), exist_ok=True)
    try:
        io_meta = execute_component(task_config)
        with open(execution_final_meta_path, "w") as fw:
            json.dump(dict(status=dict(code=0), io_meta=io_meta.dict()), fw, indent=4)
    except Exception as e:
        with open(execution_final_meta_path, "w") as fw:
            json.dump(dict(status=dict(code=-1, exceptions=traceback.format_exc())), fw)
        raise e


def load_config_from_file(configs, config_file):
    from ruamel import yaml

    if config_file is not None:
        configs.update(yaml.safe_load(config_file))
    return configs


def load_config_from_env(configs, env_name):
    import os
    from ruamel import yaml

    if env_name is not None and os.environ.get(env_name):
        configs.update(yaml.safe_load(os.environ[env_name]))
    return configs


def execute_component(config: TaskConfigSpec):
    component = load_component(config.component)
    logger.info(f"parameters： {config.parameters}")
    inputs = IOMeta.InputMeta(data={}, model={})
    outputs = IOMeta.OutputMeta(data={}, model={}, metric={})
    component.execute(config, outputs)
    return IOMeta(inputs=inputs, outputs=outputs)


def load_component(cpn_name: str):
    from fate_flow.components.components import BUILDIN_COMPONENTS

    for cpn in BUILDIN_COMPONENTS:
        if cpn.name == cpn_name:
            return cpn
