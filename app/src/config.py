import os
import yaml

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../common/configuration.yaml')
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config