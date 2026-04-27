from abc import ABC, abstractmethod

class BaseCollision(ABC):

    @abstractmethod
    def check(self, a, b) -> bool:
        pass

    @abstractmethod
    def resolve(self, a, b):
        pass