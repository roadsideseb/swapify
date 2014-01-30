=======
swapify
=======

Make South migrations in re-usable Django apps work with swappable models such
as the ``auth.User`` model.


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
