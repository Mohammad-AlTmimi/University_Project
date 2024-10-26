class CustomError(Exception):
    def __init__(self, message: str, error_code: int):
        super().__init__(message)
        self.error_code = error_code
        self.message = message

    def __str__(self):
        return f"[Error code {self.error_code}]: {self.message}"
    
