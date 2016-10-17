from django.test import TestCase


class SubmissionsViewsBaseTestCase(TestCase):
    @classmethod
    def setUpData(cls):
        pass


class TestListUserSubmissionsView(SubmissionsViewsBaseTestCase):
    def test_list_submissions(self):
        pass


class TestViewSubmissionView(SubmissionsViewsBaseTestCase):
    def test_view_submission(self):
        pass


class TestEditSubmissionView(SubmissionsViewsBaseTestCase):
    def test_edit_submission(self):
        pass


class TestDeleteSubmissionView(SubmissionsViewsBaseTestCase):
    def test_delete_submission(self):
        pass


class TestSubmitView(SubmissionsViewsBaseTestCase):
    def test_submit(self):
        pass
