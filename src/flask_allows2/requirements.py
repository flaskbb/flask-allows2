import operator
from abc import ABCMeta
from abc import abstractmethod
from collections.abc import Callable
from typing import cast

from .allows import _call_requirement
from .overrides import _current_overrides
from .typing import Identity
from .typing import RequirementType

__all__ = (
    "Requirement",
    "ConditionalRequirement",
    "C",
    "Or",
    "And",
    "Not",
)


class Requirement(metaclass=ABCMeta):
    """
    Base for object based Requirements in Flask-Allows. This is quite
    useful for requirements that have complex logic that is too much to fit
    inside of a single function.
    """

    @abstractmethod
    def fulfill(self, user: Identity) -> bool:
        """
        Abstract method called to verify the requirement against the current
        user and request.

        .. versionchanged:: 0.5.0
            Passing request is now deprecated, pending removal in version 1.0.0

        :param user: The current identity
        :param request: The current request.
        """
        return cast(bool, NotImplemented)

    def __call__(self, user: Identity) -> bool:
        return _call_requirement(self.fulfill, user)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}()>"


class ConditionalRequirement(Requirement):
    """
    Used to combine requirements together in ways other than all-or-nothing,
    such as with an or-reducer (any requirement must be True)::

        from flask_allows2 import Or

        requires(Or(user_is_admin, user_is_moderator))

    or negating a requirement::

        from flask_allows2 import Not

        requires(Not(user_logged_in))

    Combinations may also nested::

        Or(user_is_admin, And(user_is_moderator, HasPermission('view_admin')))

    Custom combinators may be built by creating an instance of ConditionalRequirement
    and supplying any combination of its keyword parameters

    This class is also exported under the ``C`` alias.


    :param requirements: Collection of requirements to combine into
        one logical requirement
    :param op: Optional, Keyword only. A binary operator that accepts two
        booleans and returns a boolean.
    :param until: Optional, Keyword only. A boolean to short circuit on (e.g.
        if provided with True, then the first True evaluation to return from a
        requirement ends verification)
    :param negated: Optional, Keyword only. If true, then the
        ConditionalRequirement will return the opposite of what it actually
        evaluated to (e.g. ``ConditionalRequirement(user_logged_in, negated=True)``
        returns False if the user is logged in)
    """

    def __init__(
        self,
        *requirements: RequirementType,
        op: Callable[[bool, bool], bool] = operator.and_,
        until: bool | None = None,
        negated: bool | None = None,
    ) -> None:
        self.requirements = requirements
        self.op = op
        self.until = until
        self.negated = negated

    @classmethod
    def And(cls, *requirements: RequirementType) -> "ConditionalRequirement":
        """
        Short cut helper to construct a combinator that uses
        :meth:`operator.and_` to reduce requirement results and stops
        evaluating on the first False.

        This is also exported at the module level as ``And``
        """
        return cls(*requirements, op=operator.and_, until=False)

    @classmethod
    def Or(cls, *requirements: RequirementType) -> "ConditionalRequirement":
        """
        Short cut helper to construct a combinator that uses
        :meth:`operator.or_` to reduce requirement results and stops evaluating
        on the first True.

        This is also exported at the module level as ``Or``
        """
        return cls(*requirements, op=operator.or_, until=True)

    @classmethod
    def Not(cls, *requirements: RequirementType) -> "ConditionalRequirement":
        """
        Shortcut helper to negate a requirement or requirements.

        This is also exported at the module as ``Not``
        """
        return cls(*requirements, negated=True)

    def fulfill(self, user: Identity) -> bool:
        reduced: bool | None = None

        requirements = self.requirements
        overrides = _current_overrides()

        if overrides is not None:
            requirements = tuple(r for r in requirements if r not in overrides)

        for r in requirements:
            result = _call_requirement(r, user)

            if reduced is None:
                reduced = result
            else:
                reduced = self.op(reduced, result)

            if self.until == reduced:
                break

        if reduced is not None:
            return not reduced if self.negated else reduced

        return True

    def __and__(self, require: RequirementType) -> "ConditionalRequirement":
        return self.And(self, require)

    def __or__(self, require: RequirementType) -> "ConditionalRequirement":
        return self.Or(self, require)

    def __invert__(self) -> "ConditionalRequirement":
        return self.Not(self)

    def __repr__(self) -> str:
        parts = []

        for name in ["op", "negated", "until"]:
            value = getattr(self, name)
            if not value:
                continue
            parts.append(f"{name}={value!r}")

        if parts:
            additional = f" {', '.join(parts)}"
        else:
            additional = ""

        return f"<{self.__class__.__name__} requirements={self.requirements!r}{additional}>"  # noqa: E501

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ConditionalRequirement)
            and self.op == other.op
            and self.until == other.until
            and self.negated == other.negated
            and self.requirements == other.requirements
        )

    def __hash__(self) -> int:
        return hash((self.requirements, self.op, self.until, self.negated))


(C, And, Or, Not) = (
    ConditionalRequirement,
    ConditionalRequirement.And,
    ConditionalRequirement.Or,
    ConditionalRequirement.Not,
)
