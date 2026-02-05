#############
Flask-Allows2
#############

Version |version| (:ref:`Change log <changelog>`)

Flask-Allows2 gives you the ability to impose identity requirements on routes
in your Flask application::


    from flask import Flask
    from flask_allows2 import Allows, Requirement
    from flask_login import current_user

    app = Flask(__name__)
    allows = Allows(app=app, identity_loader=lambda: current_user)

    class IsAdmin(Requirement):
        def requires(self, user):
            return user.permissions.get('admin')

    @app.route('/admin')
    @allows.requires(IsAdmin())
    def admin_index():
        return "Welcome to the super secret club"

************
Installation
************

Flask-Allows2 is available on `pypi <https://pypi.org/project/Flask-Allows2/>`_ and
installable with::

    pip install Flask-Allows2

Flask-Allows2 supports 3.12+.

.. note::

    If you are installing ``Flask-Allows2`` outside of a virtual environment,
    consider installing it with ``pip install --user Flask-Allows2`` rather
    than using sudo or adminstrator privileges to avoid installing it into
    your system Python.

*******
Content
*******

.. toctree::
   :maxdepth: 1

   quickstart
   requirements
   helpers
   after_the_fact
   failure
   api
   changelog
