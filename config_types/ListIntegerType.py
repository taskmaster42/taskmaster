class ListIntegerType(list):
    def __init__(self, iterable):
        super().__init__(int(item) for item in iterable)
