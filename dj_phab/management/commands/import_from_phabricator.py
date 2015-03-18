from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from django.db import transaction
from django.utils import timezone

from dj_phab.conduit import ConduitAPI
from dj_phab.importer import ImportRunner
from dj_phab.models import LastImportTracker

from phabricator import Phabricator

class Command(NoArgsCommand):
    help = u"Import user, project, repository, and diff data from Phabricator. Will import " \
           u"data updated since last import; or all data if this is the initial import"
    can_import_settings = True

    def handle_noargs(self, **options):
        # Fetch last import time
        last_import_time = LastImportTracker.get_last_import_time()

        # Set up our API connection
        conduit = ConduitAPI(Phabricator(), getattr(settings, 'IMPORT_BATCH_SIZE', 50))

        # Start a transaction; will commit on completion of block; rollback upon uncaught
        # exception
        with transaction.atomic():
            # Import data
            import_runner = ImportRunner(conduit)
            import_runner.run(last_import_time)

            # Update last import time
            LastImportTracker.update_last_import_time(timezone.now())

        self.stdout.write(u"Data successfully imported")