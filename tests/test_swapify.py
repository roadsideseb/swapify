from unittest2 import TestCase

from swapify import cli


class TestSwapifier(TestCase):

    def setUp(self):
        super(TestSwapifier, self).setUp()
        self.model = u'auth.User'
        self.swapifier = cli.Swapifier(self.model)

    def test_allows_setting_only_swappable_model(self):
        self.assertEqual(self.swapifier.app_label, u'auth')
        self.assertEqual(self.swapifier.model_name, u'User')
        self.assertEqual(self.swapifier.model, self.model)
        self.assertEqual(self.swapifier.swappable_name, u'AUTH_USER_MODEL')
        self.assertEqual(
            self.swapifier.swappable_app_label, u'AUTH_USER_APP_LABEL')
        self.assertEqual(
            self.swapifier.swappable_model_name, u'AUTH_USER_MODEL_NAME')
        self.assertEqual(
            self.swapifier.swapify_marker, u'# SWAPIFIED: AUTH_USER_MODEL')

    def test_sets_swapify_marker_correctly(self):
        sample_data = "# -*- coding: utf-8 -*-"
        marked_data = sample_data + '\n# SWAPIFIED: AUTH_USER_MODEL'

        self.assertFalse(self.swapifier.is_swapified(sample_data))
        self.assertEquals(
            self.swapifier.set_swapify_marker(sample_data), marked_data)
        self.assertTrue(self.swapifier.is_swapified(marked_data))

    def test_can_add_settings_import(self):
        sample_data = "from south.v2 import DataMigration"

        self.assertEquals(
            self.swapifier.add_settings_import(sample_data),
            sample_data + '\n' + 'from django.conf import settings')

    def test_is_not_duplicating_settings_import(self):
        sample_data = '\n'.join([
            "from south.v2 import DataMigration",
            "from django.conf import settings"])
        self.assertEquals(
            self.swapifier.add_settings_import(sample_data), sample_data)

    def test_can_add_constants(self):
        sample_data = "class Migration(SchemaMigration):"

        self.assertEqual(
            self.swapifier.add_swappable_constants(sample_data),
            '\n'.join([
                "AUTH_USER_MODEL = getattr(settings, u'AUTH_USER_MODEL', u'auth.User')",
                "AUTH_USER_APP_LABEL, AUTH_USER_MODEL_NAME = AUTH_USER_MODEL.split('.')",
                "", "", sample_data]))

    def test_can_add_dependency_without_depends_on(self):
        sample_data = "class Migration(SchemaMigration):"

        self.assertEqual(
            self.swapifier.add_dependency(sample_data),
            '\n'.join([
                sample_data, "", "    depends_on = (",
                "        (AUTH_USER_APP_LABEL, u'0001_initial'),", "    )" ,
                ""]))

    def test_can_add_dependency_with_depends_on(self):
        sample_data = "\n".join([
            "class Migration(SchemaMigration):", "    depends_on = (",
            "        ('someapp', '0001_initial'),", "    )\n"])

        self.assertEqual(
            self.swapifier.add_dependency(sample_data),
            '\n'.join([
                "class Migration(SchemaMigration):", "    depends_on = (",
                "        (AUTH_USER_APP_LABEL, u'0001_initial'),",
                "        ('someapp', '0001_initial'),", "    )" ,
                ""]))

    def test_can_replace_orm_string(self):
        sample_data = "'to': u\"orm['auth.User']\"})"
        self.assertEqual(
            self.swapifier.replace_orm_string(sample_data),
            "'to': u\"orm['{}']\".format(AUTH_USER_MODEL)})")

    def test_can_replace_model(self):
        sample_data = "u'auth.user'"
        self.assertEqual(
            self.swapifier.replace_model(sample_data), u"AUTH_USER_MODEL")

    def test_can_replace_object_name(self):
        sample_data = u"'Meta': {'object_name': 'User'},"
        self.assertEqual(
            self.swapifier.replace_object_name(sample_data),
            u"'Meta': {'object_name': AUTH_USER_MODEL_NAME},")
