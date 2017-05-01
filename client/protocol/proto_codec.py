
from cStringIO import StringIO


class Decode:
    def __init__(self, payload):
        self.payload = payload
        self.payloadio = StringIO(self.payload)
        self.request_stack = []

        self.parameters = {}

        self.__read()
        self.__cleanup_request_stack()
        self.__analyze()

    def __read(self):
        while True:
            try:
                self.request_stack.append(self.payloadio.readline())

                # Abbruch-Bedingung fuer Lesevorgang (1x New line)
                if len(self.request_stack) > 1 and self.request_stack[-1] == "\n":
                    break

            # Solange lesen bis nichts mehr verfuegbar ist
            except IOError:
                break
            # Alle anderen durchreichen
            except Exception as exc:
                raise exc

    def __cleanup_request_stack(self):
        """
        Entfernt alle Eintraege die genau ein Newline-Zeichen sind und entfernt alle Newline-Zeichen, die sich am Ende eiens strings befinden.
        :return:
        """
        current_stack = self.request_stack
        new_stack = []

        for el in current_stack:
            if el[-1] == "\n" and len(el) > 1:
                new_stack.append(el[:-1])

        self.request_stack = new_stack

    def __analyze(self):
        """
        Evaluates the previously recorded request
        :return:
        """
        if len(self.request_stack) < 1:
            raise RuntimeError()

        current_stack = self.request_stack

        method_parts = current_stack.pop(0).split(" ")
        self._request_method = method_parts.pop(0)
        self._request_method_args = method_parts

        for params in current_stack:
            # Split on first occurence
            parts = params.split(":", 1)

            # Parameters sind fehlerhaft
            if len(parts) != 2:
                raise RuntimeError()

            key = parts[0].strip()
            value = parts[1].strip()

            if not key or not value:
                raise RuntimeError()

            self.parameters[key] = value

    def get_method(self):
        return self._request_method

    def get_method_args(self):
        return self._request_method_args

    def get_params(self):
        return self.parameters


class Encode:
    def __init__(self):
        self._method = None
        self._method_args = []
        self._params = {}

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, val):
        if not isinstance(val, str):
            raise ValueError()
        self._method = val

    @property
    def method_args(self):
        return self._method_args

    @method_args.setter
    def method_args(self, val):
        if not isinstance(val, list):
            raise ValueError()
        self._method_args = val

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, val):
        if not isinstance(val, dict):
            raise ValueError()
        self._params = val

    def encode(self):
        buffer = ""

        buffer += self.method + " " + str.join(" ", self.method_args) + "\n"
        for key, value in self.params.iteritems():
            buffer += str(key) + ": " + str(value) + "\n"

        return buffer+"\n"

    def __str__(self):
        return self.encode()

    def __repr__(self):
        return self.__str__()