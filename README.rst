Flask-Allows2
=============

Are your permissions making too much noise all the time? Are your permissions
stomping all over your actual code? Are your permission decorators clawing
at your line count all the time? Think there's no answer? There is! Flask-Allows.


Flask-Allows2 is an authorization tool for Flask inspired by
`django-rest-framework <https://github.com/tomchristie/django-rest-framework>`_'s
permissioning system and `rest_condition <https://github.com/caxap/rest_condition>`_'s
ability to compose simple requirements into more complex ones.

Installation
------------

Flask-Allows2 is available on `pypi <https://pypi.org/project/Flask-Allows2/>`_ and
installable with::

    pip install Flask-Allows2

Flask-Allows2 supports 3.12+.

.. note::

    If you are installing ``Flask-Allows2`` outside of a virtual environment,
    consider installing it with ``pip install --user Flask-Allows2`` rather
    than using sudo or adminstrator privileges to avoid installing it into
    your system Python.


More Information
----------------

- For more information, `please visit the documentation <https://flask-allows2.readthedocs.io/en/latest/>`_.
- Found a bug, have a question, or want to request a feature? Here is our `issue tracker <https://github.com/flaskbb/flask-allows2/issues>`_.
- Need the source code? Here is the `repository <https://github.com/flaskbb/flask-allows2>`_
