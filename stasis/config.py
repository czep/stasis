import pathlib
import importlib

DEFAULT_CONFIG_FILE = "stasis_config.py"
BOOTSTRAP_PATH = "bootstrap"

def read_config():
    config_path = pathlib.Path(DEFAULT_CONFIG_FILE)
    if config_path.exists():
        global_vars = {}
        local_vars = {}
        with open(config_path.resolve()) as f:
            exec(f.read(), global_vars, local_vars)
        return local_vars
    else:
        return {}
