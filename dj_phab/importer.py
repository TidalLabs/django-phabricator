"""
Imports data from Phab API to Django models
"""
import datetime
from collections import namedtuple
from django.db import models, transaction
from django.utils import timezone
from dj_phab.models import PhabUser, Project, Repository, PullRequest, UpdatedFile


class MissingRequiredDataError(Exception):
    pass


class RelationNotImportedError(Exception):
    pass


class BaseImporter(object):

    def __init__(self, record, *args, **kwargs):
        super(BaseImporter, self).__init__(*args, **kwargs)
        self.record = record
        # search for an instance matching the record and assign to self.instance
        self.instance = self.find_existing_instance()

    @classmethod
    def convert_records(cls, records):
        """
        Convert a list of records received from Phab into persisted Django models

        @param list<any> records
        @return list<Model> Model instances
        """
        instances = []

        for record in records:
            importer = cls(record)
            importer.convert_record()
            instances.append(importer.instance)

        return instances

    def convert_record(self):
        raise NotImplementedError()

    def find_existing_instance(self):
        raise NotImplementedError()


class Importer(BaseImporter):
    """
    Base class for all importers that convert Phab data to Django models

    Subclasses must override `convert_record` method.
    """

    Options = namedtuple(
        'Options',
        ['phab_name', 'conversion', 'required', 'default']
    )

    def convert_record(self):
        """
        Convert a dict of data received from Phab into a Django model; save model to DB.
        If a model already exists for record with given PHID, skips processing.
        """
        # convert the data
        fields, m2ms = self.map_fields()

        # If we already have an instance, update existing record
        if self.instance:
            for field_name, value in fields.iteritems():
                if hasattr(self.instance, field_name):
                    setattr(self.instance, field_name, value)
            self.instance.save()
        else:
            # Create and save new model instance
            self.instance = self.model.objects.create(**fields)

        # And attach M2Ms
        for field_name, val_list in m2ms.iteritems():
            if hasattr(self.instance, field_name):
                setattr(self.instance, field_name, val_list)

    def find_existing_instance(self):
        """
        Search for an existing model instance for the record in question

        @return models.Model or None
        """
        try:
            return self.model.objects.get(phid=self.record['phid'])
        except KeyError:
            raise MissingRequiredDataError(u"No PHID found in %s data: %s" %
                                               (self.model._meta.verbose_name_raw, self.record))
        except self.model.DoesNotExist:
            return None

        return None

    def get_raw_value(self, field_options):
        """
        Retrieve a raw (un-converted) field value based on Phab API field name,
        fallback value, and whether the field is required

        @param Importer.Options field_options
        @return str raw value
        """
        try:
            # retrieve based on the dict key specified in options
            value = self.record[field_options.phab_name]
        except KeyError:
            value = None

        if value is not None:
            return value
        elif field_options.required:
            # required fields should result in errors if they don't exist in the record
            raise MissingRequiredDataError(u"Missing field %s in %s data: %s" %
                                               (field_options.phab_name,
                                                self.model._meta.verbose_name_raw,
                                                self.record))
        else:
            # non-required fields should use the defined default
            return field_options.default

    def convert_phab_fk(self, raw_value, model):
        try:
            return model.objects.get(phid=raw_value)
        except model.DoesNotExist:
            raise RelationNotImportedError(u"Related model of class %s with phid %s "
                                           u"not found for %s record with data: %s" %
                                           (model._meta.verbose_name_raw,
                                            raw_value,
                                            self.model._meta.verbose_name_raw,
                                            self.record))

    def convert_phab_m2m(self, raw_value, model):
        return [self.convert_phab_fk(val, model) for val in raw_value]

    def map_fields(self):
        """
        This method does the heavy lifting.
        Fill out a dict of values ready to save directly into a Django model instance,
        using the importer class's field_map attribute to retrieve appropriate
        values from the record and convert types as needed

        @return dict mapped fields
        """
        fields = {}
        m2ms = {}

        for (django_name, options) in self.field_map.iteritems():
            raw_val = self.get_raw_value(options)

            # Begin type conversion...

            # FKs / M2Ms are stored in dicts b/c we also need to know the model they reference
            try:
                fk_model = options.conversion.get('phab_fk')
                m2m_model = options.conversion.get('phab_m2m')
            except AttributeError:
                # conversion isn't defined in a dict
                fk_model = None
                m2m_model = None

            # convert raw value to correct Python type...
            # Relationships
            if m2m_model:
                val = self.convert_phab_m2m(raw_val, m2m_model)
            elif fk_model and raw_val is not None:
                try:
                    val = self.convert_phab_fk(raw_val, fk_model)
                except RelationNotImportedError:
                    if options.required:
                        raise
                    else:
                        val = None
            elif options.conversion == 'm2m':
                # We should expect a list of model instances here
                val = raw_val

            # other types
            elif options.conversion in (str, 'phid'):
                # string vals don't need conversion
                val = raw_val

            elif options.conversion == 'timestamp':
                # Timestamps need conversion to datetimes
                val = datetime.datetime.fromtimestamp(int(raw_val))
                # And saving naive ones raises warnings
                val = timezone.make_aware(val, timezone.get_current_timezone())

            elif callable(options.conversion):
                # Any callable other than `str` can be used for a custom conversion
                val = options.conversion(raw_val)
            else:
                # if all else fails
                val = raw_val

            # add it to the list of values we'll return
            if val is not None:
                if m2m_model or options.conversion == 'm2m':
                    m2ms[django_name] = val
                else:
                    fields[django_name] = val

        return fields, m2ms


class UserImporter(Importer):
    """
    Import Phab user data to Django models
    """
    model = PhabUser
    field_map = {
        'phid':      Importer.Options('phid', 'phid', True, None),
        'user_name': Importer.Options('userName', str, True, None),
        'real_name': Importer.Options('realName', str, False, 'Anonymous Coward'),
    }


class ProjectImporter(Importer):
    """
    Import Phab Project data to Django models
    """
    model = Project
    field_map = {
        'phid':    Importer.Options('phid', 'phid', True, None),
        'name':    Importer.Options('name', str, True, None),
        'phab_id': Importer.Options('id', int, True, None),
    }


class RepositoryImporter(Importer):
    model = Repository
    field_map = {
        'phid':       Importer.Options('phid', 'phid', True, None),
        'name':       Importer.Options('name', str, True, None),
        'phab_id':    Importer.Options('id', int, True, None),
        'callsign':   Importer.Options('callsign', str, False, ''),
        'monogram':   Importer.Options('monogram', str, False, ''),
        'uri':        Importer.Options('uri', str, False, ''),
        'remote_uri': Importer.Options('remoteURI', str, False, ''),
        'is_active':  Importer.Options('isActive', bool, True, True),
    }


class PullRequestImporter(Importer):
    model = PullRequest
    field_map = {
        'phid':         Importer.Options('phid', 'phid', True, None),
        'phab_id':      Importer.Options('id', int, True, None),
        'repository':   Importer.Options('repositoryPHID', {'phab_fk': Repository}, False, None),
        'files':        Importer.Options('files', 'm2m', False, None),
        'title':        Importer.Options('title', str, True, ''),
        'author':       Importer.Options('authorPHID', {'phab_fk': PhabUser}, True, None),
        'reviewers':    Importer.Options('reviewers', {'phab_m2m': PhabUser}, True, None),
        'line_count':   Importer.Options('lineCount', int, True, None),
        'status':       Importer.Options('status', int, True, None),
        'uri':          Importer.Options('uri', str, True, ''),
        'diff_count':   Importer.Options('diffs', len, True, ''),
        'commit_count': Importer.Options('commits', len, True, None),
        'date_opened':  Importer.Options('dateCreated', 'timestamp', True, None),
        'date_updated': Importer.Options('dateModified', 'timestamp', True, None),
    }


class UpdatedFileImporter(BaseImporter):
    def find_existing_instance(self):
        try:
            return UpdatedFile.objects.get(filename=self.record)
        except UpdatedFile.DoesNotExist:
            return None

    def convert_record(self):
        if not self.instance:
            self.instance = UpdatedFile.objects.create(filename=self.record)


class ImportRunner(object):
    """
    Fetches data from Phabricator and passes it off to Importer classes to convert and
    save to DB
    """

    def __init__(self, api, *args, **kwargs):
        super(ImportRunner, self).__init__(*args, **kwargs)
        self.api = api

    def run(self, last_import_time):
        """
        Execute the import
        """
        # Fetch all users
        UserImporter.convert_records(self.api.fetch_users())

        # Fetch all projects
        ProjectImporter.convert_records(self.api.fetch_projects())

        # Fetch all repos
        RepositoryImporter.convert_records(self.api.fetch_repositories())

        # Fetch diffs modified since last import
        diffs = self.api.fetch_pull_requests(modified_since=last_import_time)

        for diff in diffs:
            filenames = self.api.fetch_files(int(diff['id']))
            files = UpdatedFileImporter.convert_records(filenames)
            diff['files'] = files

        PullRequestImporter.convert_records(diffs)
