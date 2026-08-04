from collections.abc import Callable
from collections.abc import Iterator
from contextlib import contextmanager
from functools import wraps
from typing import Any
from typing import cast

from werkzeug.local import LocalProxy
from werkzeug.local import LocalStack

from .typing import RequirementType

_override_ctx_stack: LocalStack[tuple["OverrideManager", "Override"]] = LocalStack()

__all__ = ("current_overrides", "Override", "OverrideManager")


def _current_overrides() -> "Override | None":
    rv = _override_ctx_stack.top
    if rv is None:
        return None
    return rv[1]


current_overrides: "Override" = LocalProxy(_current_overrides)  # type: ignore[assignment]
"""
Proxy to the currently pushed override context.

Evaluates to ``None`` when no override context is pushed.
"""


def _isinstance[R](
    f: Callable[["Override", "Override"], R],
) -> Callable[["Override", Any], R]:
    @wraps(f)
    def check(self: "Override", other: Any) -> R:
        if not isinstance(other, Override):
            return cast(R, NotImplemented)
        return f(self, other)

    return check


class Override:
    """
    Container object that allows selectively disabling requirements.

    Requirements can be disabled by passing them to the constructor or
    by calling the ``add`` method. They can be re-enabled by calling the
    ``remove`` method. To check if a requirement is currently disabled, you
    may call either ``is_overridden`` or use ``in``.

    Override objects can be combined and compared to each other with the following
    operators:

    ``+`` creates a new overide object by combining two others, the new
    override overrides all requirements that both parents did.

    ``+=`` similar to ``+`` except it is an inplace update.

    ``-`` creates a new override instance by removing any overrides from
    the first instance that are contained in the second instance.

    ``-=`` similar to ``-`` except it is an inplace update

    ``==`` compares two overrides and returns true if both have the same
    disabled requirements.

    ``!=`` similar to ``==`` except returns true if both have different
    disabled requirements.
    """

    def __init__(self, *requirements: RequirementType) -> None:
        self._requirements: set[RequirementType] = set(requirements)

    def add(self, requirement: RequirementType, *requirements: RequirementType) -> None:
        """
        Adds one or more requirements to the override context.
        """
        self._requirements.update((requirement,) + requirements)

    def remove(
        self, requirement: RequirementType, *requirements: RequirementType
    ) -> None:
        """
        Removes one or more requirements from the override context.
        """
        self._requirements.difference_update((requirement,) + requirements)

    def is_overridden(self, requirement: RequirementType) -> bool:
        """
        Checks if a particular requirement is current overridden. Can also
        be used as ``in``::

            override = Override()
            override.add(is_admin)
            override.is_overridden(is_admin)  # True
            is_admin in override  # True

        """
        return requirement in self._requirements

    def __contains__(self, other: RequirementType) -> bool:
        return self.is_overridden(other)

    @_isinstance
    def __add__(self, other: "Override") -> "Override":
        requirements = self._requirements | other._requirements
        return Override(*requirements)

    @_isinstance
    def __iadd__(self, other: "Override") -> "Override":
        if len(other._requirements) > 0:
            self.add(*other._requirements)
        return self

    @_isinstance
    def __sub__(self, other: "Override") -> "Override":
        requirements = self._requirements - other._requirements
        return Override(*requirements)

    @_isinstance
    def __isub__(self, other: "Override") -> "Override":
        if len(other._requirements) > 0:
            self.remove(*other._requirements)
        return self

    @_isinstance
    def __eq__(self, other: "Override") -> bool:
        return self._requirements == other._requirements

    @_isinstance
    def __ne__(self, other: "Override") -> bool:
        return not self == other

    def __len__(self) -> int:
        return len(self._requirements)

    def __bool__(self) -> bool:
        return len(self) != 0

    __nonzero__ = __bool__

    def __repr__(self) -> str:
        return f"Override({self._requirements!r})"


class OverrideManager:
    """
    Used to manage the process of overriding and removing overrides.
    This class shouldn't be used directly, instead use ``allows.overrides``
    to access these controls.
    """

    def push(self, override: Override, use_parent: bool = False) -> None:
        """
        Binds an override to the current context, optionally use the
        current overrides in conjunction with this override

        If ``use_parent`` is true, a new override is created from the
        parent and child overrides rather than manipulating either
        directly.
        """
        current = self.current
        if use_parent and current:
            override = current + override

        _override_ctx_stack.push((self, override))

    def pop(self) -> None:
        """
        Pops the latest override context.

        If the override context was pushed by a different override manager,
        a ``RuntimeError`` is raised.
        """
        rv = _override_ctx_stack.pop()
        if rv is None or rv[0] is not self:
            raise RuntimeError(
                f"popped wrong override context ({rv} instead of {self})"
            )

    @property
    def current(self) -> Override | None:
        """
        Returns the current override context if set otherwise None
        """
        return _current_overrides()

    @contextmanager
    def override(
        self, override: Override, use_parent: bool = False
    ) -> Iterator[Override | None]:
        """
        Allows temporarily pushing an override context, yields the new context
        into the following block.
        """
        self.push(override, use_parent)
        yield self.current
        self.pop()
