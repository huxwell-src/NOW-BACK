from django.urls import path
from rest_framework.documentation import include_docs_urls
from . import views
from .views import UserListCreateView, UserUpdateView, UserDeleteView, ProductoListView

urlpatterns = [
    path('login', views.UserLogin.as_view(), name='login'),
    path('logout', views.UserLogout.as_view(), name='logout'),
    path('user', views.UserView.as_view(), name='user'),
    path('create', UserListCreateView.as_view(), name='user-list-create'), #GET #POST
    path('edit/<int:pk>', UserUpdateView.as_view(), name='user-update'),  #PUT
    path('delete/<int:pk>', UserDeleteView.as_view(), name='user-delete'), #DELETE
    path('productos', ProductoListView.as_view(), name='producto-list'),

    path('docs/', include_docs_urls(title="NOW Api"))
]
