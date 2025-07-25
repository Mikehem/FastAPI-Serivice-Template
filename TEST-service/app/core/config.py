#####################################################################
# Copyright(C), 2025 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import os

from typing import List

from hydra import initialize_config_dir, compose, initialize
from omegaconf import OmegaConf
from dotenv import load_dotenv

load_dotenv()
# set the base path for application access
CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))
cfg = None
# set the runtime configuration
abs_config_dir = os.path.join(CONFIG_PATH, "../", "conf")
MODE = os.environ['MODE']
with initialize(config_path= "../conf"):
    cfg = compose(config_name="config.yaml", overrides=[f"models={MODE}", f"store={MODE}", f"processing={MODE}"])
    #print(OmegaConf.to_yaml(cfg))