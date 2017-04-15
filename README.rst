=============================
swapify - Swappables in South
=============================

.. image:: https://api.travis-ci.org/elbaschid/swapify.png?branch=master
    :target: https://travis-ci.org/elbaschid/swapify?branch=master

After the custom user model was brought upon the Django community, it had all
the attention it well deserved and more and more re-usable apps are providing
support for custom user models.

I've been working with `django-oscar`_ and many of its extensions over the past
two years. Oscar added support for the custom user models in its 0.6 release
and `django-fancypages`_ even goes beyond that and leverages `the (hidden)
swappable API`_.

One of the few things that could be considered troublesome with models that are
swappable, is providing compatible South migrations. Over the last few months,
I've had to touch enough migrations and replace ``auth.User`` with
``AUTH_USER_MODEL`` to be annoyed by it and automate the situation.

Behold ``swapify``, the little commandline tool that fixes your migrations for
a swappable model of your choice (on at a time). It checks your migration
files for you swappable and updates the migrations if required.

This is a first attempt based on my own experiences. There's probably uncovered
ground and potential for improvement out there...so feedback is very welcome.

Enjoy!

.. _`django-oscar`:
.. _`django-fancypages`:
.. _`the (hidden) swappable API`: https://code.djangoproject.com/ticket/19103


Installation
------------

You can either install the latest release from PyPI::

    pip install swapify

or install the latest development version from github::

    pip install https://github.com/elbaschid/swapify/archive/master.tar.gz


Usage
-----

Get a list of all migrations in a directory that require fixing::

    swapify list myproject/ --model auth.User

Update all migrations to work with swapped models::

    swapify apply myproject/ --model auth.User

You can also test updating the files and get the output on ``stdout``::

    swapify apply myproject/ --model auth.User --dry-run

And for very custom models you can even do::

    swapify apply myproject/ --model swap.Swappable --var-name MYSWAP_SWAPPABLE_MODEL


License
-------

*swapify* is available under the MIT license.


.. image:: https://d2weczhvl823v0.cloudfront.net/elbaschid/swapify/trend.png


.. image:: https://d2weczhvl823v0.cloudfront.net/elbaschid/swapify/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

