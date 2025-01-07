from dotenv import load_dotenv
import json
import os


def update_config_file(key, value):
    config = load_config_file()
    config[key] = value
    with open("config.json", "w") as f:
        json.dump(config, f)


def load_config_file():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def create_config_file_if_not_exists():
    if not os.path.exists("config.json"):
        with open("config.json", "w") as f:
            json.dump({}, f)
