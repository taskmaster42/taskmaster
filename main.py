import yaml

from config_parser import Config


class Task():
    def __init__(self, task_name, config_file):
        self.task_name = task_name
        self.config = Config(config_file)


def main():
    with open('config_sample.yml', 'r') as file:
        config = yaml.safe_load(file)
    task_list = {}
    for task_name, config in config["programs"].items():
        task_list[task_name] = Task(task_name, config)


if __name__ == "__main__":
    main()
