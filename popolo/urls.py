from django.urls import path

from popolo.views import (
    MembershipDetailView,
    OrganizationDetailView,
    PersonDetailView,
    PostDetailView,
)


urlpatterns = [
    path('person/<int:pk>/', PersonDetailView.as_view(), name='person-detail'),
    path('organization/<int:pk>/', OrganizationDetailView.as_view(), name='organization-detail'),
    path('membership/<int:pk>/', MembershipDetailView.as_view(), name='membership-detail'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
]
