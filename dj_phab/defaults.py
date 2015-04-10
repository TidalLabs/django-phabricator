"""
Defaults for overridable settings
"""
from django.conf import settings


# Configuration for stats reporting
PHAB_STATS = {
    # diffs with this number of lines or more will not be included in averages or frequency data:
    'huge_diff_size': 2500,
    # diffs with this number of lines or fewer will not be included in averages or frequency data
    'small_diff_size': 5,
    # additional counts will be calculated of diffs with more than these number of lines:
    'xl_diff_size': 1000,
    'large_diff_size': 500,
}


IMPORT_BATCH_SIZE = 50


def get_diff_sizes():
    """
    Return default diff sizes updated with any settings overrides

    @return dict diff sizes updated with any settings overrides
    """
    diff_sizes = {}
    diff_sizes.update(PHAB_STATS)
    diff_sizes.update(getattr(settings, 'PHAB_STATS'))
    return diff_sizes
