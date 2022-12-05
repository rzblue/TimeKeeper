# pylint: disable=C0103
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class TimeSession:
    user_id: int
    start_time: datetime
    end_time_: datetime | None = None
    id: int | None = None
    total_time: timedelta | None = field(init=False, default=None)

    def __post_init__(self):
        if self.start_time and self.end_time:
            self.total_time = self.end_time - self.start_time

    @classmethod
    def from_tuple(cls, initializer: tuple[int, int, datetime, datetime]):
        (id_, user_id, start_time, end_time) = initializer
        return cls(user_id, start_time, end_time, id_)

    @property
    def end_time(self) -> datetime:
        return self.end_time_

    @end_time.setter
    def end_time(self, value: datetime):
        self.end_time_ = value

    @property
    def has_ended(self):
        return self.end_time is not None and self.start_time is not None


NullableTimeSession = TimeSession | None
