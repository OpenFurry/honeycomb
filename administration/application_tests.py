from django.test import tag

# from .models import Application
from .tests import BaseAdminTestCase


class BaseApplicationTestCase(BaseAdminTestCase):
    @classmethod
    def setUpTestCase(cls):
        super(BaseApplicationTestCase, cls).setUpTestCase()


@tag('as_user')
class TestListAllApplicationsViewAsUser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_social_mod')
class TestListAllApplicationsViewAsSocialMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_content_mod')
class TestListAllApplicationsViewAsContentMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_superuser')
class TestListAllApplicationsViewAsSuperuser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_user')
class TestListSocialApplicationsViewAsUser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_social_mod')
class TestListSocialApplicationsViewAsSocialMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_content_mod')
class TestListSocialApplicationsViewAsContentMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_superuser')
class TestListSocialApplicationsViewAsSuperuser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_user')
class TestListContentApplicationsViewAsUser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_social_mod')
class TestListContentApplicationsViewAsSocialMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_content_mod')
class TestListContentApplicationsViewAsContentMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_superuser')
class TestListContentApplicationsViewAsSuperuser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_user')
class TestCreateApplicationViewAsUser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_social_mod')
class TestCreateApplicationViewAsSocialMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_content_mod')
class TestCreateApplicationViewAsContentMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_superuser')
class TestCreateApplicationViewAsSuperuser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_user')
class TestViewApplicationViewAsUser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_social_mod')
class TestViewApplicationViewAsSocialMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_content_mod')
class TestViewApplicationViewAsContentMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_superuser')
class TestViewApplicationViewAsSuperuser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_user')
class TestListParticipatingApplicationsViewAsUser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_social_mod')
class TestListParticipatingApplicationsViewAsSocialMod(
        BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_content_mod')
class TestListParticipatingApplicationsViewAsContentMod(
        BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_superuser')
class TestListParticipatingApplicationsViewAsSuperuser(
        BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_user')
class TestClaimApplicationViewAsUser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_social_mod')
class TestClaimApplicationViewAsSocialMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_content_mod')
class TestClaimApplicationViewAsContentMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_superuser')
class TestClaimApplicationViewAsSuperuser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_user')
class TestResolveApplicationViewAsUser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_social_mod')
class TestResolveApplicationViewAsSocialMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_content_mod')
class TestResolveApplicationViewAsContentMod(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@tag('as_superuser')
class TestResolveApplicationViewAsSuperuser(BaseApplicationTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)
