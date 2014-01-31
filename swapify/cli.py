#! /usr/bin/env python
# -*- encoding: utf-8 -*-
"""
swapify - Adjust South migrations to work with custom user models.

Usage:
    swapify apply <DIR> [--model MODEL] [--var-name SWAPPABLE] [--dry-run]
    swapify list <DIR> [--model MODEL] [--var-name SWAPPABLE]

Options:
    --model         Name of the swappable model as '<app_label>.<model_name>',
                    e.g. 'auth.User'. Default: 'auth.User'
    --var-name      Variable name for the swappable model, e.g.
                    AUTH_USER_MODEL. If it is not specified it is generated
                    from the model name using <APP_LABEL>_<MODEL_NAME>_MODEL.
                    Default: AUTH_USER_MODEL.
    --dry-run       Run in test mode without changing files. Outputs to stdout.
"""
import os
import re
from docopt import docopt


SWAPIFY_MARKER = "# SWAPIFIED: {0.swappable_name}"

ENCODING_LINE_RE = re.compile(r'(# -\*- coding: utf-8 -\*-)')
MIGRATION_IMPORT_RE = re.compile(
    r'(from south.v2 import (Schema|Data)Migration)')
MIGRATION_CLASS_RE = re.compile(
    r'(class Migration\((Schema|Data)Migration\):)')
DEPENDS_ON_RE = re.compile(r'(depends_on = \()')


class Swapifier(object):

    def __init__(self, model, swappable_name=None):
        print model, swappable_name
        self.model = model  # auth.User
        self.app_label, self.model_name = self.model.split('.')

        if not swappable_name:
            swappable_name = u"{0.app_label}_{0.model_name}_MODEL".format(self)

        # e.g. AUTH_USER_MODEL
        self.swappable_name = swappable_name.upper()
        # e.g. AUTH_USER_APP_LABEL
        self.swappable_app_label = (
            u"{0.app_label}_{0.model_name}_APP_LABEL").format(self).upper()
        # e.g. AUTH_USER_MODEL_NAME
        self.swappable_model_name = u"{}_NAME".format(self.swappable_name)
        self.swapify_marker = SWAPIFY_MARKER.format(self)

        self.orm_search_string = r'u?"orm\[\'{}\'\]"'.format(self.model)

    def set_swapify_marker(self, data):
        data, __ = ENCODING_LINE_RE.subn(
            r"\1\n{}".format(self.swapify_marker), data)
        return data

    def is_swapified(self, data):
        return self.swapify_marker in data

    def add_settings_import(self, data):
        settings_import = r'from django.conf import settings'
        if settings_import in data:
            return data
        return MIGRATION_IMPORT_RE.sub(
            r"\1\n{}".format(settings_import), data)

    def add_swappable_constants(self, data):
        constants = '\n'.join([
            r"{sw_model} = getattr(settings, u'{sw_model}', u'{model}')",
            r"{sw_app_label}, {sw_model_name} = {sw_model}.split('.')"])
        constants = constants.format(
            sw_model=self.swappable_name, model=self.model,
            sw_app_label=self.swappable_app_label,
            sw_model_name=self.swappable_model_name)

        if constants in data:
            return data

        return MIGRATION_CLASS_RE.sub(
            r"{}\n\n\n\1".format(constants), data)

    def add_dependency(self, data):
        app_dependency = u"({}, u'0001_initial'),".format(
            self.swappable_app_label)

        if app_dependency in data:
            return data

        if not DEPENDS_ON_RE.search(data):
            data = MIGRATION_CLASS_RE.sub(
                r'\1\n\n    depends_on = (\n    )\n', data)

        data = DEPENDS_ON_RE.sub(
            r'\1\n        {}'.format(app_dependency), data)
        return data

    def replace_object_name(self, data):
        return data.replace(
            "'object_name': 'User'",
            "'object_name': {}".format(self.swappable_model_name))

    def replace_model(self, data):
        data, __ = re.subn(r'u?(\'|"){}(\'|")'.format(self.model),
                           self.swappable_name, data, flags=re.I)
        return data

    def replace_orm_string(self, data):
        data, __ = re.subn(
            self.orm_search_string,
            u'u"orm[\'{{}}\']".format({})'.format(self.swappable_name), data,
            flags=re.I)
        return data

    def swapify(self, data):
        if self.is_swapified(data):
            return data

        data = self.replace_orm_string(data)
        data = self.replace_model(data)
        data = self.replace_object_name(data)

        data = self.add_dependency(data)
        data = self.add_settings_import(data)
        data = self.add_swappable_constants(data)
        data = self.set_swapify_marker(data)

        return data


def get_unfixed_files(basedir, swapifier):
    unfixed_files = []
    for dirname, subdirs, files in os.walk(basedir):
        if not dirname.endswith('migrations'):
            continue

        for filename in files:
            if not filename.endswith('.py'):
                continue

            path = os.path.join(dirname, filename)
            with open(path) as infile:
                migration_data = infile.read()

            if swapifier.is_swapified(migration_data):
                continue

            if swapifier.model not in migration_data \
               or swapifier.orm_search_string in migration_data:
                continue

            unfixed_files.append(path)
    return unfixed_files


def main():
    arguments = docopt(__doc__)

    swappable_model = arguments.get('MODEL') or u'auth.User'
    var_name = arguments.get('SWAPPABLE') or None
    dirname = arguments.get('<DIR>')

    swapifier = Swapifier(swappable_model, var_name)
    unfixed_files = get_unfixed_files(dirname, swapifier)

    if arguments.get('list'):
        if not len(unfixed_files):
            print "All your migration files are good!"
            return

        print "The following files need fixing:"
        for path in unfixed_files:
            print "\t", path
        return

    for path in unfixed_files:
        with open(path) as infile:
            migration_data = infile.read()

        swapped_data = swapifier.swapify(migration_data)

        if not arguments['--dry-run']:
            print 'UPDATED:', path
            with open(path, 'w') as outfile:
                outfile.write(swapped_data)
        else:
            print '=' * 80
            print swapped_data
            print '=' * 80


if __name__ == '__main__':
    main()
