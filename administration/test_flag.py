from unittest import skip

from django.test import tag

# from .models import Flag
from .tests import BaseAdminTestCase


class BaseFlagTestCase(BaseAdminTestCase):
    @classmethod
    def setUpTestCase(cls):
        super(BaseFlagTestCase, cls).setUpTestCase()


@skip("Not implemented")
@tag('as_user')
class TestListAllFlagsViewAsUser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestListAllFlagsViewAsSocialMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestListAllFlagsViewAsContentMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestListAllFlagsViewAsSuperuser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestListSocialFlagsViewAsUser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestListSocialFlagsViewAsSocialMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestListSocialFlagsViewAsContentMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestListSocialFlagsViewAsSuperuser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestListContentFlagsViewAsUser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestListContentFlagsViewAsSocialMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestListContentFlagsViewAsContentMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestListContentFlagsViewAsSuperuser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestCreateFlagViewAsUser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestCreateFlagViewAsSocialMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestCreateFlagViewAsContentMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestCreateFlagViewAsSuperuser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestViewFlagViewAsUser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestViewFlagViewAsSocialMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestViewFlagViewAsContentMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestViewFlagViewAsSuperuser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestListParticipatingFlagsViewAsUser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestListParticipatingFlagsViewAsSocialMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestListParticipatingFlagsViewAsContentMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestListParticipatingFlagsViewAsSuperuser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestClaimFlagViewAsUser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestClaimFlagViewAsSocialMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestClaimFlagViewAsContentMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestClaimFlagViewAsSuperuser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestResolveFlagViewAsUser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestResolveFlagViewAsSocialMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestResolveFlagViewAsContentMod(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestResolveFlagViewAsSuperuser(BaseFlagTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)
