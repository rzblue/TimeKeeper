# pylint: disable=C0103
from dataclasses import dataclass


@dataclass
class User:
    name: str
    id_string: str
    id: int | None = None

    @classmethod
    def from_tuple(cls, initializer: tuple[int, str, str]):
        (key, name, id_string) = initializer
        return cls(name, id_string, key)


NullableUser = User | None
