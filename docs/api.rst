.. _api:

#################
Flask-Allows2 API
#################

Extension
=========
.. autoclass:: flask_allows2.allows.Allows
    :members:

Permission Helper
=================

.. autoclass:: flask_allows2.permission.Permission
    :members:

Requirements Base Classes
=========================

.. autoclass:: flask_allows2.requirements.Requirement
    :members:

.. autoclass:: flask_allows2.requirements.ConditionalRequirement
    :members:


Override Management
===================

.. autoclass:: flask_allows2.overrides.Override
    :members:

.. autoclass:: flask_allows2.overrides.OverrideManager
    :members:


.. autoclass:: flask_allows2.additional.Additional
    :members:

.. autoclass:: flask_allows2.additional.AdditionalManager
    :members:


Utilities
=========

.. autofunction:: flask_allows2.views.requires
.. autofunction:: flask_allows2.views.exempt_from_requirements
.. autofunction:: flask_allows2.views.guard_entire
.. autofunction:: flask_allows2.requirements.wants_request
