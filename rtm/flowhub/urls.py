from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ListView.as_view(), name="flowhub.flow_list"),
    url(r"^uncts/", views.UnctsView.as_view(), name="flowhub.flow_uncts"),
    url(r"^my-org/$", views.MyOrgListView.as_view(), name="flowhub.my_org_flow_list"),
    url(r"^create/", views.CreateView.as_view(), name="flowhub.flow_create"),
    url(r"^(?P<flow>[0-9]+)/download/$", views.DownloadView.as_view(), name="flowhub.flow_download"),
    url(r"^(?P<flow>[0-9]+)/stars/$", views.StarView.as_view(), name="flowhub.flow_star"),
    url(r"^(?P<flow>[0-9]+)/update/$", views.EditView.as_view(), name="flowhub.flow_update"),
    url(r"^(?P<flow>[0-9]+)/delete/$", views.DeleteView.as_view(), name="flowhub.flow_delete"),
    url(r"^(?P<flow>[0-9]+)/info/$", views.InfoView.as_view(), name="flowhub.flow_info"),
    url(r"^global/$", views.ListGlobalView.as_view(), name="flowhub.flow_list_global"),
    url(r"^create-global/$", views.CreateGlobalView.as_view(), name="flowhub.flow_create_global"),
    url(r"^(?P<flow>[0-9]+)/update-global/$", views.EditGlobalView.as_view(), name="flowhub.flow_update_global"),
]