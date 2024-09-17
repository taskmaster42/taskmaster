import yaml

def main():
    with open('config_sample.yml', 'r') as file:
        config = yaml.safe_load(file)
    # print(config)
    for program, value in config["programs"].items():
        print(program)
        print(value)

if __name__ == "__main__":
    main()