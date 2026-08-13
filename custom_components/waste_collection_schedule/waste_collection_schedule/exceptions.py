"""Exceptions a source can raise to report a bad argument.

Upstream carried eight classes here, most of them variants that attach
suggestion lists so the config flow can offer a pick-list. This fork's single
source raises exactly one of them, so the rest were removed along with the
config-flow machinery that consumed them.
"""

from typing import Any


class SourceArgumentException(Exception):
    """A source argument is invalid.

    The config flow reports `message` against the field named `argument`, so
    `argument` must match the parameter name in `Source.__init__` exactly.
    """

    def __init__(self, argument: str, message: str) -> None:
        self._argument = argument
        self.message = message
        super().__init__(self.message)

    @property
    def argument(self) -> str:
        return self._argument


class SourceArgumentNotFound(SourceArgumentException):
    """A source argument was well-formed but matched nothing upstream."""

    def __init__(
        self,
        argument: str,
        value: Any,
        message_addition: str = "please check the spelling and try again.",
    ) -> None:
        self._simple_message = (
            f"We could not find values for the argument '{argument}' "
            f"with the value '{value}'"
        )
        self.message = self._simple_message
        if message_addition:
            self.message += f", {message_addition}"
        super().__init__(argument, self.message)

    @property
    def simple_message(self) -> str:
        return self._simple_message
