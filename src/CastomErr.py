class CustomErr(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class HTTPError(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code
