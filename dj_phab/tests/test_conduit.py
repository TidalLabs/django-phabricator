import datetime
from django.test import TestCase
from django.utils import timezone
from dj_phab.conduit import ConduitAPI
from dj_phab.models import PhabUser, Project, Repository, PullRequest
from dj_phab.tests import _test_data as test_data

class TestConduitAPI(TestCase):
    def setUp(self):
        # Mock the data we get back from Phab
        self.phabricator = test_data.prep_phab_mocks()

        # use a batch size of 2 so we can test batching with small data sets
        self.conduit = ConduitAPI(self.phabricator, 2)

    def test_smoke(self):
        pass

    def test_fetch_users(self):
        users = self.conduit.fetch_users()
        self.assertEqual(len(users), 3)
        bob_list = filter(lambda user: user['userName'] == 'bob', users)
        self.assertEqual(len(bob_list), 1)
        self.assertEqual(bob_list[0]['realName'], 'Bob Bobberann')

    def test_fetch_projects(self):
        projects = self.conduit.fetch_projects()
        self.assertEqual(len(projects), 5)
        lex_list = filter(lambda project: project['id'] == '13', projects)
        self.assertEqual(len(lex_list), 1)
        self.assertEqual(lex_list[0]['name'], 'LexCorp')

    def test_fetch_repositories(self):
        repos = self.conduit.fetch_repositories()
        self.assertEqual(len(repos), 5)
        anvil_list = filter(lambda repo: repo['callsign'] == 'ANV', repos)
        self.assertEqual(len(anvil_list), 1)
        self.assertEqual(anvil_list[0]['name'], 'Anvil')

    def test_fetch_all_pull_requests(self):
        prs = self.conduit.fetch_pull_requests()
        self.assertEqual(len(prs), 5)
        lightbox_list = filter(lambda pr: pr['id'] == '1465', prs)
        self.assertEqual(len(lightbox_list), 1)
        self.assertIn('clicking outside of lightbox', lightbox_list[0]['title'])

    def test_fetch_modified_pull_requests(self):
        prs = self.conduit.fetch_pull_requests(
            modified_since=datetime.datetime.fromtimestamp(1426606600))
        self.assertEqual(len(prs), 3)
        statuses_list = filter(lambda pr: pr['id'] == '1460', prs)
        self.assertEqual(len(statuses_list), 1)
        self.assertIn('Sync channel status', statuses_list[0]['title'])

        statuses_list = filter(lambda pr: pr['id'] == '1462', prs)
        self.assertEqual(len(statuses_list), 0)
