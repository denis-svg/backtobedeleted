from abc import ABC, abstractmethod

class AuthManagerInterface(ABC):
    @abstractmethod
    def loginUser(self, request):
        pass

    @abstractmethod
    def registerUser(self, request):
        pass

    @abstractmethod
    def tokenRequired(self, token):
        pass