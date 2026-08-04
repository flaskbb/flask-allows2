from collections.abc import Callable
from typing import Any

__all__ = ("Identity", "OnFail", "RequirementType", "Throws")

type Identity = Any
"""The object that represents the current user.

Flask-Allows2 never inspects the identity itself, it only hands it to the
requirements, so it may be any object at all.
"""

type RequirementType = Callable[[Identity], bool]
"""Anything that can be used as a requirement.

Either a plain callable that accepts the current identity and returns a
boolean, or an instance of :class:`~flask_allows2.requirements.Requirement`
which is callable in the same way.
"""

type OnFail = Any
"""A callable invoked when authorization fails, or a value to return as-is.

Callables are invoked with the arguments the guarded view was called with, a
non-callable is wrapped so that it is simply returned. Returning ``None``
lets the failure progress to raising :data:`Throws`.
"""

type Throws = type[Exception] | Exception
"""The exception type that is raised when authorization fails."""
