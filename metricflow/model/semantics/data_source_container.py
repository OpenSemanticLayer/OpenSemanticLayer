from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

T = TypeVar("T")


class DataSourceContainer(ABC, Generic[T]):  # noqa: D
    @abstractmethod
    def get(self, data_source_name: str) -> T:  # noqa: D
        pass

    @abstractmethod
    def values(self) -> List[T]:  # noqa: D
        pass

    @abstractmethod
    def keys(self) -> List[str]:  # noqa: D
        pass

    @abstractmethod
    def __contains__(self, item: str) -> bool:  # noqa: D
        pass

    @abstractmethod
    def put(self, key: str, value: T) -> None:  # noqa: D
        pass
