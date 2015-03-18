import datetime
from django.test import TestCase
from django.utils import timezone
from dj_phab.models import PhabUser, Project, Repository, PullRequest
from dj_phab.importer import UserImporter, ProjectImporter, RepositoryImporter, \
                             PullRequestImporter

# Create your tests here.
class TestImporter(TestCase):
    def test_smoke(self):
        pass


class TestUserImporter(TestCase):
    noemi_dict = {
        u'userName': u'noemi',
        u'phid': u'PHID-USER-7ij7ij7ij7ij7ij7ij7i',
        u'realName': u'Noemi Millman',
        u'roles': [u'admin', u'verified', u'approved', u'activated'],
        u'image': u'https://tid.al/images/tidal_logo_w.png',
        u'uri': u'http://www.example.com/noemi/'
    }
    luke_dict = {
        u'userName': u'luke',
        u'phid': u'PHID-USER-123',
        u'realName': u'Luke Skywalker',
        u'roles': [u'verified', u'approved', u'activated'],
        u'image': None,
        u'uri': u'http://www.example.com/p/luke/'
    }

    def test_smoke(self):
        pass

    def test_convert_record(self):
        self.assertEqual(PhabUser.objects.count(), 0)

        UserImporter(self.noemi_dict).convert_record()

        self.assertEqual(PhabUser.objects.count(), 1)
        noemi = PhabUser.objects.get(user_name='noemi')
        self.assertEqual(noemi.real_name, 'Noemi Millman')

    def test_convert_records(self):
        self.assertEqual(PhabUser.objects.count(), 0)

        UserImporter.convert_records([self.noemi_dict, self.luke_dict])

        self.assertEqual(PhabUser.objects.count(), 2)
        noemi = PhabUser.objects.get(user_name='noemi')
        luke = PhabUser.objects.get(user_name='luke')
        self.assertEqual(noemi.real_name, 'Noemi Millman')
        self.assertEqual(luke.real_name, 'Luke Skywalker')


class TestProjectImporter(TestCase):
    proj_1_dict = {
        u'dateCreated': u'1398434918',
        u'dateModified': u'1405951963',
        u'id': u'6',
        u'members': [
            u'PHID-USER-drlaw5eyiedluxi3xo6k',
            u'PHID-USER-qletroekoublafrle60i',
            u'PHID-USER-wlasti9ziaflexlatrla',
            u'PHID-USER-qluphoa89i3yiaslepoe',
            u'PHID-USER-jou0luhlawlupriavoes',
            u'PHID-USER-sp7aphoarl8tiasoazoe',
        ],
        u'name': u'Initech',
        u'phid': u'PHID-PROJ-th1ephiatho84toeyouf',
        u'slugs': [u'initech.net_relaunch',],
    }
    proj_2_dict = {
        u'id': u'7',
        u'name': u'Acme Inc.',
        u'phid': u'PHID-PROJ-123',
    }

    def test_smoke(self):
        pass

    def test_convert_record(self):
        self.assertEqual(Project.objects.count(), 0)

        ProjectImporter(self.proj_1_dict).convert_record()

        self.assertEqual(Project.objects.count(), 1)
        initech = Project.objects.get(phab_id=6)
        self.assertEqual(initech.name, 'Initech')

    def test_convert_records(self):
        self.assertEqual(Project.objects.count(), 0)

        ProjectImporter.convert_records([self.proj_1_dict, self.proj_2_dict])

        self.assertEqual(Project.objects.count(), 2)
        initech = Project.objects.get(phab_id=6)
        acme = Project.objects.get(phab_id=7)
        self.assertEqual(initech.name, 'Initech')
        self.assertEqual(acme.name, 'Acme Inc.')


class TestRepositoryImporter(TestCase):
    repo_1_dict = {
        "id"          : "5",
        "name"        : "Theme: Initech",
        "phid"        : "PHID-REPO-gi4fi8qiuyiam9udroes",
        "callsign"    : "INIT",
        "monogram"    : "rINIT",
        "vcs"         : "git",
        "uri"         : "http:\/\/www.example.com\/diffusion\/INIT\/",
        "remoteURI"   : "git@github.com:example\/theme-initech.git",
        "description" : "",
        "isActive"    : True,
        "isHosted"    : False,
        "isImporting" : False
    }
    repo_2_dict = {
        "id"          : "4",
        "name"        : "Sirius Cybernetics",
        "phid"        : "PHID-REPO-9lu5rouvieyievluylus",
        "callsign"    : "SCY",
        "monogram"    : "rSCY",
        "vcs"         : "git",
        "uri"         : "http:\/\/www.example.com\/diffusion\/SCY\/",
        "remoteURI"   : "git@github.com:example\/Sirius.git",
        "description" : "",
        "isActive"    : True,
        "isHosted"    : False,
        "isImporting" : False
    }

    def test_smoke(self):
        pass

    def test_convert_record(self):
        self.assertEqual(Repository.objects.count(), 0)

        RepositoryImporter(self.repo_1_dict).convert_record()

        self.assertEqual(Repository.objects.count(), 1)
        initech = Repository.objects.get(phab_id=5)
        self.assertEqual(initech.name, 'Theme: Initech')

    def test_convert_records(self):
        self.assertEqual(Repository.objects.count(), 0)

        RepositoryImporter.convert_records([self.repo_1_dict, self.repo_2_dict])

        self.assertEqual(Repository.objects.count(), 2)
        initech = Repository.objects.get(phab_id=5)
        sirius = Repository.objects.get(phab_id=4)
        self.assertEqual(initech.name, 'Theme: Initech')
        self.assertEqual(sirius.name, 'Sirius Cybernetics')


class TestPullRequestImporter(TestCase):
    diff_1_dict = {
        u'sourcePath': None,
        u'reviewers': [
            u'PHID-USER-7ij7ij7ij7ij7ij7ij7i',
            u'PHID-USER-123',
        ],
        u'lineCount': u'21',
        u'repositoryPHID': u'PHID-REPO-gi4fi8qiuyiam9udroes',
        u'id': u'628',
        u'authorPHID': u'PHID-USER-123',
        u'title': u'Change Stuff',
        u'activeDiffPHID': u'PHID-DIFF-xiediacri2brledlachl',
        u'branch': None,
        u'dateModified': u'1414515472',
        u'status': u'3',
        u'testPlan': u'Do stuff',
        u'commits': [u'PHID-CMIT-plu5o5thlebiaslexiap'],
        u'dateCreated': u'1414433294',
        u'hashes': [
            [u'gtcm', u'8aad45f66bd2dbe94ea8953d1be581b65abdcf65'],
            [u'gttr', u'1985b3817cf84528b0822864c09cb6445c3a25e8']
        ],
        u'diffs': [u'1578', u'1561', u'1557', u'1527'],
        u'phid': u'PHID-DREV-hie2hlaswiafoethoasp',
        u'auxiliary': {u'phabricator:depends-on': [], u'phabricator:projects': []},
        u'uri': u'http://www.example.com/D628',
        u'ccs': [u'PHID-USER-b6iepoethlas3iufriap'],
        u'summary': u'',
        u'arcanistProjectPHID': None,
        u'statusName': u'Closed'
    }

    def setUp(self):
        UserImporter.convert_records([TestUserImporter.noemi_dict,
                                      TestUserImporter.luke_dict])
        ProjectImporter.convert_records([TestProjectImporter.proj_1_dict,
                                         TestProjectImporter.proj_2_dict])
        RepositoryImporter.convert_records([TestRepositoryImporter.repo_1_dict,
                                            TestRepositoryImporter.repo_2_dict])

    def test_smoke(self):
        pass

    def test_convert_record(self):
        self.assertEqual(PullRequest.objects.count(), 0)

        PullRequestImporter(self.diff_1_dict).convert_record()

        self.assertEqual(PullRequest.objects.count(), 1)
        change = PullRequest.objects.get(phab_id=628)
        self.assertEqual(change.title, 'Change Stuff')
        self.assertEqual(change.author.user_name, 'luke')
        self.assertEqual(change.repository.name, 'Theme: Initech')
        self.assertEqual(change.line_count, 21)
        self.assertEqual(change.commit_count, 1)
        self.assertEqual(change.diff_count, 4)
        self.assertEqual(change.status, PullRequest.STATUS.closed)
        self.assertEqual(change.date_updated, datetime.datetime(2014, 10, 28, 16, 57, 52, 0,
                                                                timezone.get_current_timezone()))

        reviewer_usernames = [reviewer.user_name for reviewer in change.reviewers.all()]
        self.assertItemsEqual(reviewer_usernames, ['noemi', 'luke',])
