.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://img.shields.io/pypi/v/collective.feedback.svg
    :target: https://pypi.python.org/pypi/collective.feedback/
    :alt: Latest Version
.. image:: https://img.shields.io/pypi/status/collective.feedback.svg
    :target: https://pypi.python.org/pypi/collective.feedback
    :alt: Egg Status
.. image:: https://img.shields.io/pypi/pyversions/collective.feedback.svg?style=plastic
    :target: https://pypi.python.org/pypi/collective.feedback
    :alt: Supported - Python Versions
.. image:: https://img.shields.io/pypi/l/collective.feedback.svg
    :target: https://pypi.python.org/pypi/collective.feedback/
    :alt: License


===================
collective.feedback
===================

Feedback mechanism integration for volto.
Requires volto-feedback >= 0.6.0

Users can add vote and a comment to every page on the site.

Bot protection
==============

This product use `collective.honeypot <https://pypi.org/project/collective.honeypot/>`_ to prevent bot submissions.

You just need to set two environment variables:

- *EXTRA_PROTECTED_ACTIONS feedback-add*
- *HONEYPOT_FIELD xxx*

xxx should be a field name that bot should compile.

If you get hacked, you could simply change that variable.

Permissions
===========

There are two new specific permission:

- collective.feedback.ManageFeedbacks (collective.feedback: Manage Feedbacks) Allows to reset data (by default Manager and Site Administrator).
- collective.feedback.AccessFeedbacks (collective.feedback: Access Feedbacks) Allows users to list feedbacks on contents where they have that permission (by default Editor, Manager and Site Administrator)
- collective.feedback.ShowDeletedFeedbacks (collective.feedback: Show Deleted Feedbacks) Allows manager to see feedbacks of deleted objects

Feedbacks catalog
=================

Reviews are stored inside an internal catalog (based on `souper.plone <https://pypi.org/project/souper.plone/>`_).

You can access/edit data through restapi routes (see below) or through a Plone utility::

    from zope.component import getUtility
    from collective.feedback.interfaces import ICollectiveFeedbackStore

    tool = getUtility(ICollectiveFeedbackStore)

Add a vote
----------

- Method ``add``
- Parameters: ``data`` (dictionary with parameters)
- Response: unique-id of new record
- Context: only the navigation root

``data`` should be a dictionary with the following parameters:

- uid [required]: the uid of the Plone content
- vote [required]: the vote
- answer: a custom string, like a comment
- title: the title of the Plone content
- comment: an optional comment
- content: path of the object or name of the view

Others parameters will be ignored.

Search reviews
--------------

- Method ``search``
- Parameters: ``query`` (dictionary with parameters), ``sort_index`` (default=date), ``reverse`` (default=False)
- Response: a list of results

``query`` is a dictionary of indexes where perform the search.

Right now data is not indexed so search filters does not work. You only need to call search method to get all data.


List update
-----------

PATCH
~~~~~

This endpoint allows update feedbacks by list.
By now you can only change "read" property


Example::

    curl http://localhost:8080/Plone/@feedback-list \
        -X PATCH \
        -H 'Accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
            "101010101": {"read": true},
        }'


Installation
------------

Install collective.feedback by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.feedback


and then running ``bin/buildout``

Contribute
------------

- Issue Tracker: https://github.com/RedTurtle/collective.feedback/issues
- Source Code: https://github.com/RedTurtle/collective.feedback

Compatibility
=============

This product has been tested on Plone 6

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/
