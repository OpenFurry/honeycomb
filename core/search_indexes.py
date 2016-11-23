from django.utils import timezone
from haystack import indexes

from submissions.models import Submission


class SubmissionIndex(indexes.SearchIndex, indexes.Indexable):
    """The search index for submissions."""
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='owner')
    pub_date = indexes.DateTimeField(model_attr='ctime')

    def get_model(self):
        return Submission

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            ctime__lte=timezone.now())
