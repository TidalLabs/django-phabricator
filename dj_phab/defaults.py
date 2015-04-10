"""
Defaults for overridable settings
"""
from django.conf import settings


# Configuration for stats reporting
DIFF_SIZES = {
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
    diff_sizes.update(DIFF_SIZES)
    diff_sizes.update(getattr(settings, 'PHAB_STATS', {}).get('DIFF_SIZES', {}))
    return diff_sizes

def get_batch_size():
    """
    Get import batch size, optionally overridden by settings

    @return int import batch size
    """
    return getattr(settings, 'PHAB_STATS', {}).get('IMPORT_BATCH_SIZE', IMPORT_BATCH_SIZE)
