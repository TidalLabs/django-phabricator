"""
Note: we're using the model_utils TimeStampedModel to record the date the record in the
*local* DB was created/modified, not the one in Phabricator's primary DB.

Where we also store created/modified fields corresponding to data in the Phabricator DB,
we give those fields different names (e.g. "date_opened" and "date_updated" for PullRequest)
"""

from django.db import models
from dj_phab.queryset import DateGroupingQuerySet
from model_utils import Choices
from model_utils.models import TimeStampedModel


class PhabModel(models.Model):
    phid = models.CharField(max_length=30, unique=True)

    class Meta:
        abstract = True


class PhabUser(TimeStampedModel, PhabModel):
    user_name = models.CharField(max_length=255, unique=True)
    real_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.real_name

    class Meta:
        ordering = ['real_name',]


class Project(TimeStampedModel, PhabModel):
    phab_id = models.IntegerField()
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name',]


class Repository(TimeStampedModel, PhabModel):
    phab_id = models.IntegerField()
    name = models.CharField(max_length=255)
    callsign = models.CharField(max_length=16, help_text=u"Abbreviated, unique name")
    monogram = models.CharField(max_length=16, help_text=u"Version of callsign used for references in markup")
    uri = models.URLField(help_text=u"URL to access on Phabricator")
    remote_uri = models.CharField(max_length=255, help_text=u"URI of origin repo")
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u"Repositories"
        ordering=['callsign',]


class UpdatedFile(TimeStampedModel):
    """
    A file referenced in a diff
    """
    filename = models.CharField(max_length=255, unique=True) # If we have file paths longer than 255, we have other problems!

    def __unicode__(self):
        return self.filename


class PullRequestQuerySet(DateGroupingQuerySet):
    """
    Custom queryset/manager utility methods for PullRequest.  Warning: business logic!
    """

    def size_and_frequency_by_granularity(self, granularity):
        """
        Group data by time period based on granularity; annotate with mean line count
        (``avg_lines``) and total number of reviews (``review_count``) per period;
        filter by "closed" status.

        @param 'year'|'month'|'week'|'day' granularity Time period to group by
        @return QuerySet
        """
        return self.filter(status=PullRequest.STATUS.closed)\
                   .group_by_date('date_opened', granularity)\
                   .annotate(**{
                        'avg_lines': models.Avg('line_count'),
                        'review_count': models.Count('id'),
                    })


class PullRequestBaseManager(models.Manager):
    pass


class PullRequest(TimeStampedModel, PhabModel):
    STATUS = Choices(
        (0, 'needs_review', u"Needs Review"),
        (1, 'needs_revision', u"Needs Revision"),
        (2, 'accepted', u"Accepted"),
        (3, 'closed', u"Closed"),
        (4, 'abandoned', u"Abandoned"),
        (5, 'changes_planned', u"Changes Planned"),
        (0, 'in_preparation', u"In Preparation"),
    )

    phab_id = models.IntegerField()
    repository = models.ForeignKey(Repository, null=True, blank=True)
    files = models.ManyToManyField(UpdatedFile, related_name='diffs')
    title = models.CharField(max_length=255)
    author = models.ForeignKey(PhabUser)
    reviewers = models.ManyToManyField(PhabUser, related_name='reviews')
    line_count = models.PositiveIntegerField()
    status = models.SmallIntegerField(choices=STATUS)
    uri = models.URLField()
    diff_count = models.PositiveSmallIntegerField()
    commit_count = models.PositiveSmallIntegerField()
    date_opened = models.DateTimeField()
    date_updated = models.DateTimeField()

    objects = PullRequestBaseManager.from_queryset(PullRequestQuerySet)()

    def __unicode__(self):
        return self.d_id()

    def d_id(self):
        return u"D%s" % self.phab_id

    def abbrev_title(self):
        return self.title[:32]

    class Meta:
        ordering = ['-date_opened',]


class LastImportTracker(models.Model):
    """
    This is a singleton -- only one row permitted.
    """
    last_import_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.pk = 1
        super(LastImportTracker, self).save()

    @classmethod
    def get_last_import_time(cls):
        try:
            return cls.objects.get(pk=1).last_import_time
        except cls.DoesNotExist:
            return None

    @classmethod
    def update_last_import_time(cls, new_time):
        try:
            tracker = cls.objects.get(pk=1)
        except cls.DoesNotExist:
            tracker = cls()
        tracker.last_import_time = new_time
        tracker.save()
