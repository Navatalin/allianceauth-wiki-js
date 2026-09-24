from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ObjectDoesNotExist
from django.test import RequestFactory, TestCase

from allianceauth.tests.auth_utils import AuthUtils

from .auth_hooks import WikiJSService
from .manager import WikiJSManager, get_wikijs_email, map_group_name
from .models import WikiJs

MODULE_PATH = 'wikijs'
DEFAULT_AUTH_GROUP = 'Member'


def add_permissions():
    permission = Permission.objects.get(codename='access_wikijs')
    members = Group.objects.get_or_create(name=DEFAULT_AUTH_GROUP)[0]
    AuthUtils.add_permissions_to_groups([permission], [members])


class GroupNameMappingTestCase(TestCase):
    def test_maps_wiki_admin_to_administrators(self):
        self.assertEqual(map_group_name('Wiki-Admin'), 'Administrators')
        self.assertEqual(WikiJSManager._sanitize_groupname('Wiki-Admin'), 'Administrators')

    def test_preserves_other_group_names(self):
        self.assertEqual(map_group_name('Member'), 'Member')


class WikiJSEmailTestCase(TestCase):
    def setUp(self):
        self.user = AuthUtils.create_member('member_user')
        AuthUtils.add_main_character_2(
            self.user,
            'Main Character',
            90000001,
            disconnect_signals=True,
        )

    def test_uses_main_character_id(self):
        self.user.email = 'private@example.com'

        self.assertEqual(get_wikijs_email(self.user), '90000001@wiki.invalid')

    def test_requires_main_character(self):
        user = AuthUtils.create_user('no_character')

        with self.assertRaisesMessage(ValueError, 'A main character is required'):
            get_wikijs_email(user)

    def test_create_uses_generated_email(self):
        manager = WikiJSManager.__new__(WikiJSManager)
        manager._client = mock.Mock()
        manager._client.execute.side_effect = [
            '{"data": {"users": {"create": {"responseResult": {"succeeded": true}}}}}',
            '{"data": {"users": {"search": [{"id": 3, "email": "90000001@wiki.invalid"}]}}}',
        ]

        with mock.patch.object(manager, '_WikiJSManager__generate_group_list', return_value=[]):
            result = manager._WikiJSManager__create_user(self.user, password='password')

        self.assertEqual(result, 3)
        create_variables = manager.client.execute.call_args_list[0].kwargs['variables']
        search_variables = manager.client.execute.call_args_list[1].kwargs['variables']
        self.assertEqual(create_variables['email'], '90000001@wiki.invalid')
        self.assertEqual(search_variables['char_email'], '90000001@wiki.invalid')

    def test_update_uses_generated_email(self):
        WikiJs.objects.create(user=self.user, uid=3)
        manager = WikiJSManager.__new__(WikiJSManager)
        manager._client = mock.Mock()
        manager._client.execute.return_value = '{"data": {"users": {"update": {"responseResult": {"succeeded": true}}}}}'

        with mock.patch.object(manager, '_WikiJSManager__generate_group_list', return_value=[]):
            self.assertTrue(manager.update_user(self.user))

        variables = manager.client.execute.call_args.kwargs['variables']
        self.assertEqual(variables['email'], '90000001@wiki.invalid')
        self.assertNotIn(self.user.email, variables.values())


class WikiJSHooksTestCase(TestCase):
    def setUp(self):
        self.member = 'member_user'
        member = AuthUtils.create_member(self.member)
        member.email = 'private@example.com'
        member.save()
        AuthUtils.add_main_character_2(member, 'Main Character', 90000001, disconnect_signals=True)
        WikiJs.objects.create(user=member, uid=3)
        self.none_user = 'none_user'
        self.none_user = AuthUtils.create_user(self.none_user)
        self.service = WikiJSService
        self.del_user = 'del_user'
        self.del_user = AuthUtils.create_user(self.del_user)
        add_permissions()

    def test_has_account(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)
        self.assertTrue(service.user_has_account(member))
        self.assertFalse(service.user_has_account(none_user))

    def test_service_enabled(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        none_user = User.objects.get(username=self.none_user)

        self.assertTrue(service.service_active_for_user(member))
        self.assertFalse(service.service_active_for_user(none_user))

    def test_delete_user_with_no_wiki(self):  # this doesn't fail properly on sqlite investigate more tests on mysql/psql
        User.objects.get(username=self.del_user).delete()

    @mock.patch(MODULE_PATH + '.manager.WikiJSManager._update_user')
    def test_update_user(self, disable):
        disable.execute.return_value = True
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        self.assertTrue(service.update_groups(member))
        self.assertTrue(disable.called)

    @mock.patch(MODULE_PATH + '.manager.WikiJSManager._update_user')
    def test_update_non_user(self, disable):
        disable.execute.return_value = True
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.none_user)
        self.assertFalse(service.update_groups(member))
        self.assertFalse(disable.called)

    @mock.patch(MODULE_PATH + '.manager.WikiJSManager._update_user')
    def test_update_all_users(self, disable):
        disable.execute.return_value = True
        service = self.service()
        # Test member is not deleted
        service.update_all_groups()
        self.assertEqual(disable.call_count, 1)

    @mock.patch(MODULE_PATH + '.manager.WikiJSManager.client')
    def test_validate_user(self, disable):
        disable.execute.return_value = '{"data": {"users": {"deactivate": {"responseResult": {"succeeded": true}}}}}'
        service = self.service()
        # Test member is not deleted
        member = User.objects.get(username=self.member)
        service.validate_user(member)
        self.assertTrue(member.wikijs)

        # Test none user is deleted
        none_user = User.objects.get(username=self.none_user)
        WikiJs.objects.create(user=none_user, uid=4)
        service.validate_user(none_user)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username=self.none_user).wikijs

    @mock.patch(MODULE_PATH + '.manager.WikiJSManager.client')
    def test_delete_user(self, disable):
        disable.execute.return_value = '{"data": {"users": {"deactivate": {"responseResult": {"succeeded": true}}}}}'
        member = User.objects.get(username=self.member)
        service = self.service()
        result = service.delete_user(member)

        self.assertTrue(result)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username=self.member).wikijs

    def test_render_services_ctrl(self):
        service = self.service()
        member = User.objects.get(username=self.member)
        request = RequestFactory().get('/services/')
        request.user = member

        response = service.render_services_ctrl(request)
        self.assertTemplateUsed(service.service_ctrl_template)
        self.assertIn('href="%s"' % settings.WIKIJS_URL, response)
        self.assertIn('90000001@wiki.invalid', response)
        self.assertNotIn(member.email, response)
