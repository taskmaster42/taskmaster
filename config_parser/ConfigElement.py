class ConfigElement():
    def __init__(self, value, expected_type):
        self.value = expected_type(value)

    def get_value(self):
        return self.value
