"""
@author: Arno
@created: 2023-05-18
@modified: 2023-08-19

Custom errors for Requests
"""


class RemoteError(Exception):
    """Thrown when a remote API can't be reached or throws unexpected error"""

    def __init__(self, message: str = "", error_code: int = 0):
        """
        Set error code with default 0 to not make it optional and always have an integer value.
        message: Error message for the error
        error_code: The error code of the http response if relevant
        """
        self.error_code = error_code
        super().__init__(message)


class TransactionValueNotFoundError(Exception):
    """Thrown when the value of a transaction is not found in the response
    of a get transactions request"""
