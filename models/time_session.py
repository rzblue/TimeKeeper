# pylint: disable=C0103

from datetime import datetime, timedelta


class TimeSession:
    def __init__(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime | None,
        id_: int = int | None,
    ):
        self.__user_id: int = user_id
        self.__start_time: datetime = start_time
        self.__end_time: datetime = end_time
        if start_time and end_time:
            self.__total_time: timedelta = end_time - start_time
        else:
            self.__total_time = None
        self.__id: int = id_

    @classmethod
    def from_tuple(cls, initializer: tuple[int, int, datetime, datetime]):
        (id_, user_id, start_time, end_time) = initializer
        return cls(user_id, start_time, end_time, id_)

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def start_time(self) -> datetime:
        return self.__start_time

    @property
    def end_time(self) -> datetime:
        return self.__end_time

    @end_time.setter
    def end_time(self, end_time: datetime):
        if end_time > self.__start_time:
            self.__end_time = end_time
            self.__total_time = end_time - self.__start_time

    @property
    def total_time(self) -> timedelta:
        return self.__total_time

    @property
    def has_ended(self):
        return self.__end_time is not None and self.__start_time is not None

    def __str__(self):
        return (
            f"TimeSession(id: {self.id}, user_id={self.user_id}, "
            f"start_time={self.start_time}, end_time={self.end_time},"
            f" total_time={self.total_time})"
        )


NullableTimeSession = TimeSession | None
