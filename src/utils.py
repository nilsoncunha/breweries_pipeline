import yaml

class YAMLReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                return data
        except FileNotFoundError:
            print(f"File {self.file_path} not found")
            return None
        except yaml.YAMLError as e:
            print(f"Error on reading YAML file {self.file_path}: {e}")
            return None
