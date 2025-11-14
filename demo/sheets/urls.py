from django.urls import path
from . import views

app_name = "sheets"

urlpatterns = [
    # Define your app-specific routes here
    path('', views.home_view, name='home_view'),  # view route
    path('read-sheet/', views.read_sheet_view, name='read_sheet_view'),  # view route
]

api_v1 = lambda v: 'api/v1/'+v
urlpatterns += [
    path(api_v1('read-sheet'), views.read_sheet_api_controller, name='read_sheet_api_controller'),  # api route
]