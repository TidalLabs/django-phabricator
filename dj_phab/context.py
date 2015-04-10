"""
Context processors specific to dj_phab
"""

from dj_phab.defaults import get_granularities

def djp_context(request):
    return { 'granularities': get_granularities(), }
