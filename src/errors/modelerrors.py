"""
@author: Arno
@created: 2023-08-09
@modified: 2023-08-18

Custom errors for Models
"""


class WalletAddressTypeError(Exception):
    """Thrown when a address type not valid"""


class WalletIdError(Exception):
    """Thrown when a wallet has no id"""


class ChildAddressTypeError(Exception):
    """Thrown when a child address type not valid"""
