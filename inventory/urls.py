from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),  
    path("login/", views.login, name="login"),  
    path("",views.ProductListView.as_view(), name="list"),   
    path("<int:pk>/",views.ProductDetailView.as_view(), name="detail"),
    path("create-product/",views.ProductCreateView.as_view(), name="create"),
    path("change-password/",views.ChangePasswordView.as_view(), name="change-password"),
    path("<int:pk>/update-product/",views.ProductUpdateView.as_view(), name="update-product"),
    path("<int:pk>/delete-product/",views.ProductDeleteView.as_view(), name="delete-product"),
    path("search-product/",views.search, name="search-product"),
    path("sales/",views.SalesAnalyticsView.as_view(), name="sales")
    
    
]