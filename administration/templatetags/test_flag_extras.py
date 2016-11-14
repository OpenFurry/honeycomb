from .flag_extras import can_view_flagged_item
from administration.test_flag import ExistingFlagBaseTestCase


class TestCanViewFlaggedItem(ExistingFlagBaseTestCase):
    def test_failure(self):
        self.assertFalse(
            can_view_flagged_item(self.social_mod, self.active_content_flag))

    def test_participant(self):
        self.active_content_flag.participants.add(self.user)
        self.assertTrue(
            can_view_flagged_item(self.user, self.active_content_flag))

    def test_social_perms(self):
        self.assertTrue(
            can_view_flagged_item(self.social_mod, self.active_social_flag))

    def test_content_perms(self):
        self.assertTrue(
            can_view_flagged_item(self.content_mod, self.active_content_flag))
