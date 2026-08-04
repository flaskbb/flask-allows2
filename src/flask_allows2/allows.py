from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from collections.abc import Sequence
from functools import wraps
from itertools import chain
from typing import Any
from typing import cast
from typing import Literal
from typing import overload
from typing import TypeVar

from flask import current_app
from flask import Flask
from flask import Response
from werkzeug.datastructures import ImmutableDict
from werkzeug.exceptions import Forbidden

from .additional import Additional
from .additional import AdditionalManager
from .overrides import Override
from .overrides import OverrideManager
from .typing import Identity
from .typing import OnFail
from .typing import RequirementType
from .typing import Throws

__all__ = ["Allows"]

_F = TypeVar("_F", bound=Callable[..., Any])


class Allows:
    """
    The Flask-Allows extension object used to control defaults and drive
    behavior.

    :param app: Optional. Flask application instance.
    :param identity_loader: Optional. Callable that will load the current user
    :param throws: Optional. Exception type to raise by default when
        authorization fails.
    :param on_fail: Optional. A value to return or function to call when
        authorization fails.
    """

    def __init__(
        self,
        app: Flask | None = None,
        identity_loader: Callable[[], Identity] | None = None,
        throws: Throws = Forbidden,
        on_fail: OnFail = None,
    ) -> None:
        self._identity_loader = identity_loader
        self.throws = throws

        self.on_fail = _make_callable(on_fail)
        self.overrides = OverrideManager()
        self.additional = AdditionalManager()

        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initializes the Flask-Allows object against the provided application
        """
        if not hasattr(app, "extensions"):  # pragma: no cover
            app.extensions = {}
        app.extensions["allows"] = self

        @app.before_request
        def start_context(*a: Any, **k: Any) -> None:
            self.overrides.push(Override())
            self.additional.push(Additional())

        @app.after_request
        def cleanup(response: Response) -> Response:
            self.clear_all_overrides()
            self.clear_all_additional()
            return response

    def requires(
        self,
        *requirements: RequirementType,
        identity: Identity = None,
        on_fail: OnFail = None,
        throws: Throws | None = None,
    ) -> Callable[[_F], _F]:
        """
        Decorator to enforce requirements on routes

        :param requirements: Collection of requirements to impose on view
        :param identity: Optional, keyword only. An identity to use in place
            of the currently loaded identity.
        :param throws: Optional, keyword only. Exception to throw for this
            route, if provided it takes precedence over the exception stored
            on the instance
        :param on_fail: Optional, keyword only. Value or function to use as
            the on_fail for this route, takes precedence over the on_fail
            configured on the instance.
        """

        def decorator(f: _F) -> _F:
            @wraps(f)
            def allower(*args: Any, **kwargs: Any) -> Any:
                result = self.run(
                    requirements,
                    identity=identity,
                    on_fail=on_fail,
                    throws=throws,
                    f_args=args,
                    f_kwargs=kwargs,
                )

                # authorization failed
                if result is not None:
                    return result

                return f(*args, **kwargs)

            return cast(_F, allower)

        return decorator

    def identity_loader(self, f: Callable[[], Identity]) -> Callable[[], Identity]:
        """
        Used to provide an identity loader after initialization of the
        extension.

        Can be used as a method::

            allows.identity_loader(lambda: a_user)

        Or as a decorator::

            @allows.identity_loader
            def load_user():
                return a_user


        If an identity loader is provided at initialization, this method
        will overwrite it.

        :param f: Callable to load the current user
        """
        self._identity_loader = f
        return f

    def fulfill(
        self,
        requirements: Iterable[RequirementType],
        identity: Identity = None,
    ) -> bool:
        """
        Checks that the provided or current identity meets each requirement
        passed to this method.

        This method takes into account both additional and overridden
        requirements, with overridden requirements taking precedence::

            allows.additional.push(Additional(Has('foo')))
            allows.overrides.push(Override(Has('foo')))

            allows.fulfill([], user_without_foo)  # return True

        :param requirements: The requirements to check the identity against.
        :param identity: Optional. Identity to use in place of the current
            identity.
        """
        if not identity and self._identity_loader is not None:
            identity = self._identity_loader()

        all_requirements: Iterable[RequirementType]
        additional = self.additional.current

        if additional:
            all_requirements = chain(iter(additional), requirements)
        else:
            all_requirements = iter(requirements)

        overrides = self.overrides.current

        if overrides is not None:
            all_requirements = (r for r in all_requirements if r not in overrides)

        return all(_call_requirement(r, identity) for r in all_requirements)

    def clear_all_overrides(self) -> None:
        """
        Helper method to remove all override contexts, this is called automatically
        during the after request phase in Flask. However it is provided here
        if override contexts need to be cleared independent of the application
        context.

        If an override context is found that originated from an OverrideManager
        instance not controlled by the Allows object, a ``RuntimeError``
        will be raised.
        """
        while self.overrides.current is not None:
            self.overrides.pop()

    def clear_all_additional(self) -> None:
        """
        Helper method to remove all additional contexts, this is called
        automatically during the after request phase in Flask. However it is
        provided here if additional contexts need to be cleared independent of
        the request cycle.

        If an additional context is found that originated from an
        AdditionalManager instance not controlled by the Allows object, a
        ``RuntimeError`` will be raised.
        """
        while self.additional.current is not None:
            self.additional.pop()

    def run(
        self,
        requirements: Iterable[RequirementType],
        identity: Identity = None,
        throws: Throws | None = None,
        on_fail: OnFail = None,
        f_args: Sequence[Any] = (),
        f_kwargs: Mapping[str, Any] = ImmutableDict(),
        use_on_fail_return: bool = True,
    ) -> Any:
        """
        Used to preform a full run of the requirements and the options given,
        this method will invoke on_fail and/or throw the appropriate exception
        type. Can be passed arguments to call on_fail with via f_args (which are
        passed positionally) and f_kwargs (which are passed as keyword).

        :param requirements: The requirements to check
        :param identity: Optional. A specific identity to use for the check
        :param throws: Optional. A specific exception to throw for this check
        :param on_fail: Optional. A callback to invoke after failure,
            alternatively a value to return when failure happens
        :param f_args: Positional arguments to pass to the on_fail callback
        :param f_kwargs: Keyword arguments to pass to the on_fail callback
        :param use_on_fail_return: Boolean (default True) flag to determine
            if the return value should be used. If true, the return value
            will be considered, else failure will always progress to
            exception raising.
        """

        throws = throws or self.throws
        on_fail = _make_callable(on_fail) if on_fail is not None else self.on_fail

        if not self.fulfill(requirements, identity):
            result = on_fail(*f_args, **f_kwargs)
            if use_on_fail_return and result is not None:
                return result
            raise throws

        return None


@overload
def _get_allows() -> Allows: ...


@overload
def _get_allows(app: Flask | None, silent: Literal[True]) -> Allows | None: ...


def _get_allows(app: Flask | None = None, silent: bool = False) -> Allows | None:
    """Gets the application-specific Allows data.

    :param app: The Flask application. Defaults to the current app.
    :param silent: If set to True, it will return ``None`` instead of raising
                   a ``RuntimeError``.
    """
    if app is None:
        app = current_app

    if silent and (not app or "allows" not in app.extensions):
        return None

    if "allows" not in app.extensions:
        raise RuntimeError("Flask-Allows2 not configured against current app")

    allows: Allows = app.extensions["allows"]
    return allows


def _make_callable(func_or_value: OnFail) -> Callable[..., Any]:
    if not callable(func_or_value):
        return lambda *a, **k: func_or_value
    return cast(Callable[..., Any], func_or_value)


def _call_requirement(requirement: RequirementType, user: Identity) -> bool:
    return requirement(user)
