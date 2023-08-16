"""
@author: Arno
@created: 2023-08-09
@modified: 2023-08-16

Custom errors for Models
"""


class WalletAddressTypeError(Exception):
    """Thrown when a address type not valid"""


class ChildAddressTypeError(Exception):
    """Thrown when a child address type not valid"""
