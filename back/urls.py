from django.urls import path

from back import views

urlpatterns = [
    path('backu', views.home, name='home'),
    path('', views.index, name='index'),
    path('done/<str:id>', views.done, name='done'),
    path('notfound/', views.notfound, name='notfound'),
]


