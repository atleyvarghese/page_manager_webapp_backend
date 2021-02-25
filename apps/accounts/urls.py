from django.urls import path

from apps.accounts.views import UserAuthenticateView, FacebookPageListView, FacebookPageView

urlpatterns = [
    path('facebook/authenticate/', UserAuthenticateView.as_view(), name='facebook-authenticate'),
    path('facebook/page-list/', FacebookPageListView.as_view(), name='facebook-page-list'),
    path('facebook/page/<int:id>/', FacebookPageView.as_view(), name='facebook-page'),
]
