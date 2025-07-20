from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def get(self, index):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, index, item):
        pass

    @abstractmethod
    def delete(self, index):
        pass
