import yaml

def load_settings(file_path):
    with open(file_path, 'r') as stream:
        try:
            settings = yaml.safe_load(stream)
            return settings
        except yaml.YAMLError as exc:
            print(f"Error loading YAML file: {exc}")

file_path = 'settings.yml'
settings = load_settings(file_path)