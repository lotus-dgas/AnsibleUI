

from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url, include
from django.urls import path

from restful import views

urlpatterns = format_suffix_patterns([
    url(r'^$', views.api_root),
    url(r'^users/$', views.UserList.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user-detail'),

    url(r'hostslists/$', views.HostsListsList.as_view(), name='hostslists-list'),
    url(r'hostslists/(?P<pk>[0-9]+)/$', views.HostsListsDetail.as_view(), name='hostslists-detail'),
])

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
