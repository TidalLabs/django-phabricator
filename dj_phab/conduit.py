import time

class ConduitAPI(object):
    # @TODO: convert Python-formatted args to JSON-formatted ones
    # @TODO: handle failure cases
    """
    Wrapper around `python-phabricator` API client to provide access to Conduit
    data with syntax less dependent on Conduit.
    """

    def __init__(self, phabricator, batch_size=50, **kwargs):
        """
        @param Phabricator phabricator A python-phabricator API client
        @param int batch_size Limit number of records returned in any one request
        """
        # @TODO: update definitions
        super(ConduitAPI, self).__init__(**kwargs)
        self.phabricator = phabricator
        self.batch_size = batch_size

    def fetch_users(self, **kwargs):
        return self.phabricator.user.query(**kwargs).response

    def fetch_projects(self, **kwargs):
        # @TODO: handle case where N > 100, since phab returns these batched
        response = self.phabricator.project.query(**kwargs).response
        return response.get('data', {}).values()

    def fetch_repositories(self, **kwargs):
        return self.phabricator.repository.query(**kwargs).response

    def fetch_pull_requests(self, modified_since=None, **kwargs):
        """
        This is a mess because you can ask Conduit to sort returned data by date modified
        (descending) but you can't filter by the field.  Plus we have enough total data
        and will normally be updating such a small subset of it that it's worth fetching
        in batches.

        @param datetime.datetime modified_since If not None, only diffs modified after this
            date will be returned
        @return list<dict>
        """
        pull_requests = []
        options = kwargs
        options['limit'] = self.batch_size
        options['offset'] = 0

        # If since is not None, order by date modified
        if modified_since:
            # we need a UNIX timestamp form of the date
            min_timestamp = int(time.mktime(modified_since.timetuple()))
            options['order'] = 'order-modified'

        # I wish Python supported do...while
        # fetch in batches until no data or date modified < modified_since
        while True:
            new_data = self.phabricator.differential.query(**options).response

            if modified_since:
                # Remove any items that predate our min date modified
                new_data = [item for item in new_data if int(item['dateModified']) >= min_timestamp]

            # hang onto the data if we have any
            if len(new_data):
                pull_requests.extend(new_data)
                # update offset so next fetch gets the next batch
                options['offset'] += len(new_data)

            if (len(new_data) < self.batch_size):
                # we're out of data. stop fetching
                break

        return pull_requests