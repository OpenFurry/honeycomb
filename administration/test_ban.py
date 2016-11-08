from unittest import skip

from django.test import tag

# from .models import Ban
from .tests import BaseAdminTestCase


class BaseBanTestCase(BaseAdminTestCase):
    @classmethod
    def setUpTestCase(cls):
        super(BaseBanTestCase, cls).setUpTestCase()


@skip("Not implemented")
@tag('as_user')
class TestListBansViewAsUser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestListBansViewAsSocialMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestListBansViewAsContentMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestListBansViewAsSuperuser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestCreateBanViewAsUser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestCreateBanViewAsSocialMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestCreateBanViewAsContentMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestCreateBanViewAsSuperuser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestViewBanViewAsUser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestViewBanViewAsSocialMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestViewBanViewAsContentMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestViewBanViewAsSuperuser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestListParticipatingBansViewAsUser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestListParticipatingBansViewAsSocialMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestListParticipatingBansViewAsContentMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestListParticipatingBansViewAsSuperuser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_user')
class TestLiftBanViewAsUser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_social_mod')
class TestLiftBanViewAsSocialMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_content_mod')
class TestLiftBanViewAsContentMod(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)


@skip("Not implemented")
@tag('as_superuser')
class TestLiftBanViewAsSuperuser(BaseBanTestCase):
    def test_it_works(self):
        self.assertEqual(1+1, 2)
