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
    path("sales/",views.SalesAnalyticsView.as_view(), name="sales"),
    path("create-category/",views.CategoryCreateView.as_view(), name="create-category"),
    path("list-category/",views.CategoryListView.as_view(), name="list-category"),
    path("<int:pk>/delete-category/",views.CategoryDeleteView.as_view(), name="delete-category"),
    path("list-sale/",views.SalesListView.as_view(), name="list-sale"),
    path("create-sale/",views.SalesCreateView.as_view(), name="create-sale"),
    path("<int:pk>/delete-sale/",views.SalesDeleteView.as_view(), name="delete-sale"),
    
    
]