from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import settings

urlpatterns = patterns('',
    # Example:
    # (r'^(static|media)/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PAGES}),
    (r'^$', 'webapp.views.index'),
    (r'^upload_file/?$', 'webapp.views.upload_file'),
    (r'^leadfile/(?P<leadfileno>\d+)$', 'webapp.views.show_leadfile'),
    (r'^leads/(?P<qdate>[\d\-]+)$', 'webapp.views.show_leadsperday'),
    (r'^delete/leadfile/(?P<leadfileno>\d+)$', 'webapp.views.delete_leadfile'),
    (r'^lead/(?P<leadno>\d+)$', 'webapp.views.show_lead'),
    (r'^lead/ucfld$', 'webapp.views.save_field_value'),
    (r'^post/(?P<consumer_name>moss|ia)/(?P<leadno>\d+)$', 'webapp.views.post_lead'),
    (r'^lead/(?P<consumer_name>moss|ia)/ufld/?', 'webapp.views.save_required_field_value'),
    (r'^lead/(?P<consumer_name>moss|ia)/new/?', 'webapp.views.new_lead'),
    (r'^lead/delete/?', 'webapp.views.delete_lead'),
    (r'^fopt/?', 'webapp.views.get_options'),
    (r'^lead/new_group/?', 'webapp.views.new_group'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEV_MODE:
    urlpatterns += patterns('',
                            (r'^(static|media)/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PAGES}),
                            )