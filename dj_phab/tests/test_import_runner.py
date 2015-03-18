import datetime
from django.test import TestCase
from django.utils import timezone
from dj_phab.conduit import ConduitAPI
from dj_phab.importer import ImportRunner
from dj_phab.models import PhabUser, Project, Repository, PullRequest
from dj_phab.tests import _test_data as test_data

class TestImportRunner(TestCase):
    def setUp(self):
        phabricator = test_data.prep_phab_mocks()
        # set batch size to 2 to support small data sets
        conduit = ConduitAPI(phabricator, 2)
        self.runner = ImportRunner(conduit)

    def test_smoke(self):
        pass

    def test_run_all(self):
        self.assertEqual(PhabUser.objects.count(), 0)
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(Repository.objects.count(), 0)
        self.assertEqual(PullRequest.objects.count(), 0)

        self.runner.run(None)

        self.assertEqual(PhabUser.objects.count(), 3)
        self.assertEqual(Project.objects.count(), 5)
        self.assertEqual(Repository.objects.count(), 5)
        self.assertEqual(PullRequest.objects.count(), 5)

    def test_run_since(self):
        self.assertEqual(PhabUser.objects.count(), 0)
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(Repository.objects.count(), 0)
        self.assertEqual(PullRequest.objects.count(), 0)

        self.runner.run(datetime.datetime.fromtimestamp(1426606600))

        self.assertEqual(PhabUser.objects.count(), 3)
        self.assertEqual(Project.objects.count(), 5)
        self.assertEqual(Repository.objects.count(), 5)
        self.assertEqual(PullRequest.objects.count(), 3)