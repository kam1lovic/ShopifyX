from django.contrib.auth.views import LogoutView
from django.urls import path, include

from apps.views import ProductListView, ProductDetailView, OrderFormView, LoginFormView, \
    OrderListView, UserProfileUpdateView, MarketListView, StreamCreateView, StreamListView, StatisticTemplateView, \
    WishlistListView

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('market', MarketListView.as_view(), name='market_list'),
    path('stream', StreamCreateView.as_view(), name='create_stream'),
    path('list-stream', StreamListView.as_view(), name='stream_list'),
    path('order-create', OrderFormView.as_view(), name='order_create'),
    path('order-list', OrderListView.as_view(), name='order_list'),
    path('statistic', StatisticTemplateView.as_view(), name='statistic'),
    path('profile', UserProfileUpdateView.as_view(), name='profile'),
    path('wishlist', WishlistListView.as_view(), name='wishlist'),
    path('login/', LoginFormView.as_view(), name='login_page'),
    path('logout', LogoutView.as_view(next_page='product_list'), name='logout'),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file")
]


