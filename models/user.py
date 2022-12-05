# pylint: disable=C0103


class User:
    def __init__(self, name: str, id_string: str, id_=None):
        self.id_: int | None = id_
        self.__name = name
        self.__id_string = id_string

    @classmethod
    def from_tuple(cls, initializer: tuple[int, str, str]):
        (key, name, id_string) = initializer
        return cls(name, id_string, key)

    @property
    def id(self):
        return self.id_

    @id.setter
    def id(self, value):
        self.id_ = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def id_string(self):
        return self.__id_string

    @id_string.setter
    def id_string(self, value):
        self.__id_string = value

    def __str__(self):
        return f"User({self.id}, {self.name}, {self.id_string})"


NullableUser = User | None
