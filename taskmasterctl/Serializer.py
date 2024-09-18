import pickle


class Serializer():
    @staticmethod
    def serialize(data: dict) -> bytes:
        return pickle.dumps(data)

    @staticmethod
    def deserialize(data: bytes) -> dict:
        if not data:
            return {}
        return pickle.loads(data)
