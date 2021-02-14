class ValueObserver:
    def __init__(self, value: float):
        self._value = value
        self._observers = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        for callback in self._observers:
            callback(self._value)

    def register_observer(self, callback):
        self._observers.append(callback)