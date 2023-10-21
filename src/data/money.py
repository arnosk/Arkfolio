"""
@author: Arno
@created: 2023-05-09
@modified: 2023-10-21

Money datatype
From: https://github.com/py-moneyed/py-moneyed/blob/master/src/moneyed/classes.py

"""
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, NoReturn, Protocol, TypeVar  # , Self

log = logging.getLogger(__name__)


def force_decimal(amount: object) -> Decimal:
    """Given an amount of unknown type, type cast it to be a Decimal."""
    if not isinstance(amount, Decimal):
        return Decimal(str(amount))
    return amount


class MoneyComparisonError(TypeError):
    # This exception was needed often enough to merit its own
    # Exception class.

    def __init__(self, other: object) -> None:
        assert not isinstance(other, Money)
        self.other = other

    def __str__(self) -> str:
        return f"Cannot compare instances of Money and {self.other.__class__.__name__}"


class CurrencyDoesNotExist(Exception):
    def __init__(self, code: str | None) -> None:
        super().__init__(f"No currency with code {code} is defined.")


class SupportsNeg(Protocol):
    def __neg__(self) -> Any:
        ...


# This TypeVar is used for methods on Money that return self, so that subclasses become
# accurately typed as returning instances of the subclass, not Money itself.
# From python 3.11 from typing import Self can be used!
M = TypeVar("M", bound="Money")


@dataclass
class Money:
    amount_cents: int = 0
    decimal_places: int = 18
    precision: int = 2
    currency_symbol: str = ""

    def __post_init__(self):
        self.multiplier = 10**self.decimal_places

    @property
    def amount(self) -> Decimal:
        return self.amount_cents / self.multiplier

    @classmethod
    def mint(
        cls,
        amount: Decimal | float,
        decimal_places: int = 18,
        precision: int = 2,
        currency_symbol: str = "$",
    ):  # -> Self:
        return cls(
            int(amount * (10**decimal_places)),
            decimal_places,
            precision,
            currency_symbol,
        )

    def __repr__(self) -> str:
        return f"Money('{self.amount_cents}', '{self.decimal_places}', '{self.currency_symbol}')"

    def __str__(self) -> str:
        return format_money(self)

    def __hash__(self) -> int:
        return hash((self.amount_cents, self.decimal_places, self.currency_symbol))

    def __pos__(self: M) -> M:
        return self.__class__(
            amount_cents=self.amount_cents,
            decimal_places=self.decimal_places,
            precision=self.precision,
            currency_symbol=self.currency_symbol,
        )

    def __neg__(self: M) -> M:
        return self.__class__(
            amount_cents=-self.amount_cents,
            decimal_places=self.decimal_places,
            precision=self.precision,
            currency_symbol=self.currency_symbol,
        )

    def __add__(self: M, other: object) -> M:
        if other == 0:
            # This allows things like 'sum' to work on list of Money instances,
            # just like list of Decimal.
            return self
        if not isinstance(other, Money):
            return NotImplemented
        if (
            self.currency_symbol == other.currency_symbol
            and self.decimal_places == other.decimal_places
        ):
            return self.__class__(
                amount_cents=self.amount_cents + other.amount_cents,
                decimal_places=self.decimal_places,
                precision=self.precision,
                currency_symbol=self.currency_symbol,
            )

        raise TypeError(
            "Cannot add or subtract two Money instances with different currencies or nr of decimal places"
        )

    def __sub__(self: M, other: SupportsNeg) -> M:
        return self.__add__(-other)

    def __rsub__(self: M, other: object) -> M:
        return (-self).__add__(other)

    def __mul__(self: M, other: object) -> M:
        if isinstance(other, Money):
            raise TypeError("Cannot multiply two Money instances.")
        else:
            if isinstance(other, float):
                log.warn(
                    "Multiplying Money instances with floats is deprecated",
                    DeprecationWarning,
                )
            return self.__class__(
                amount_cents=int(self.amount_cents * force_decimal(other)),
                decimal_places=self.decimal_places,
                precision=self.precision,
                currency_symbol=self.currency_symbol,
            )

    def __truediv__(self: M, other: object) -> M | Decimal:
        if isinstance(other, Money):
            if (
                self.currency_symbol != other.currency_symbol
                or self.decimal_places != other.decimal_places
            ):
                raise TypeError(
                    "Cannot divide two different currencies or different nr of decimal places"
                )
            return Decimal(self.amount_cents / other.amount_cents)
        else:
            if isinstance(other, float):
                log.warn(
                    "Dividing Money instances by floats is deprecated",
                    DeprecationWarning,
                )
            return self.__class__(
                amount_cents=int(self.amount_cents / force_decimal(other)),
                decimal_places=self.decimal_places,
                precision=self.precision,
                currency_symbol=self.currency_symbol,
            )

    def __rtruediv__(self, other: object) -> NoReturn:
        raise TypeError("Cannot divide non-Money by a Money instance.")

    def __abs__(self: M) -> M:
        return self.__class__(
            amount_cents=abs(self.amount_cents),
            decimal_places=self.decimal_places,
            precision=self.precision,
            currency_symbol=self.currency_symbol,
        )

    def __bool__(self) -> bool:
        return bool(self.amount_cents)

    def __rmod__(self: M, other: object) -> M:
        """
        Calculate percentage of an amount.  The left-hand side of the
        operator must be a numeric value.

        Example:
        >>> money = Money(200, 'USD')
        >>> 5 % money
        Money('10', 'USD')
        """
        if isinstance(other, Money):
            raise TypeError("Invalid __rmod__ operation")
        else:
            if isinstance(other, float):
                log.warn(
                    "Calculating percentages of Money instances using floats is deprecated",
                    DeprecationWarning,
                )
            return self.__class__(
                amount_cents=int(Decimal(str(other)) * self.amount_cents / 100),
                decimal_places=self.decimal_places,
                precision=self.precision,
                currency_symbol=self.currency_symbol,
            )

    __radd__ = __add__
    __rmul__ = __mul__

    # _______________________________________
    # Override comparison operators
    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Money)
            and self.amount_cents == other.amount_cents
            and self.decimal_places == other.decimal_places
            and self.currency_symbol == other.currency_symbol
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        return not result

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            raise MoneyComparisonError(other)
        if (
            self.currency_symbol == other.currency_symbol
            and self.decimal_places == other.decimal_places
        ):
            return self.amount_cents < other.amount_cents
        else:
            raise TypeError("Cannot compare Money with different currencies.")

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            raise MoneyComparisonError(other)
        if (
            self.currency_symbol == other.currency_symbol
            and self.decimal_places == other.decimal_places
        ):
            return self.amount_cents > other.amount_cents
        else:
            raise TypeError("Cannot compare Money with different currencies.")

    def __le__(self, other: object) -> bool:
        return self < other or self == other

    def __ge__(self, other: object) -> bool:
        return self > other or self == other


def format_money(money: Money) -> str:
    return f"{money.currency_symbol} {money.amount:.{money.precision}f}"
