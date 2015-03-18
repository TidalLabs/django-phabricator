from django.contrib import admin
from dj_phab.models import PhabUser, Project, Repository, PullRequest, LastImportTracker


class PhabUserAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'real_name', 'phid',]
    list_display_links = ['user_name', 'real_name',]
    search_fields = ['user_name', 'real_name', 'phid',]


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'phid', 'phab_id',]
    list_display_links = ['name',]
    search_fields = ['name', 'phid',]


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'callsign', 'is_active', 'phid',]
    list_display_links = ['name', 'callsign',]
    search_fields = ['name', 'callsign', 'phid',]
    list_filter = ['is_active',]


class PullRequestAdmin(admin.ModelAdmin):
    list_display = ['phab_id', 'abbrev_title', 'repository', 'author', 'status',
                    'line_count', 'date_opened', 'phid',]
    list_display_links = ['phab_id', 'abbrev_title',]
    search_fields = ['title', 'phid',]
    list_filter = ['author', 'reviewers', 'status', 'repository',]
    date_filter = 'date_opened'


class LastImportTrackerAdmin(admin.ModelAdmin):
    list_display = ['last_import_time',]
    list_display_links = []


admin.site.register(PhabUser, PhabUserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(LastImportTracker, LastImportTrackerAdmin)