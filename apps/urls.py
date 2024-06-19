from django.contrib.auth.views import LogoutView
from django.urls import path, include

from apps.views import ProductListView, ProductDetailView, OrderFormView, LoginFormView, \
    OrderListView, UserProfileUpdateView, MarketListView, StreamCreateView, StreamListView, StatisticListView, \
    WishlistView, SuccessOrderTemplateView, WishlistListView, UserProfileImageUpdateView, \
    UserChangePasswordFormView, OperatorTemplateView, CompetitionListView, PaymentFormView, DiagramTemplateView, \
    RemoveFromWishlistView, LoginFromTelegramBotTemplateView, LoginCheckView, PaymentInfoListView

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),

    path('product/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),

    path('market', MarketListView.as_view(), name='market_list'),

    path('stream/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('stream', StreamCreateView.as_view(), name='create_stream'),
    path('stream-list', StreamListView.as_view(), name='stream_list'),

    path('order-create', OrderFormView.as_view(), name='order_create'),

    path('order-list', OrderListView.as_view(), name='order_list'),
    path('order-success/<int:pk>', SuccessOrderTemplateView.as_view(), name='success_order'),

    path('statistic', StatisticListView.as_view(), name='statistic'),

    path('profile', UserProfileUpdateView.as_view(), name='profile'),
    path('profile-image', UserProfileImageUpdateView.as_view(), name='profile_image'),
    path('profile-password-update', UserChangePasswordFormView.as_view(), name='password_update'),

    path('operator', OperatorTemplateView.as_view(), name='operator'),

    path('competition', CompetitionListView.as_view(), name='competition'),

    path('payment', PaymentFormView.as_view(), name='payment'),
    path('payment-info', PaymentInfoListView.as_view(), name='payment_info'),

    path('diagram', DiagramTemplateView.as_view(), name='diagram'),

    path('add-wishlist/<slug:product_slug>', WishlistView.as_view(), name='add_wishlist'),
    path('remove-from-wishlist/<slug:product_slug>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('list-wishlist', WishlistListView.as_view(), name='wishlist'),

    path('login/', LoginFormView.as_view(), name='login_page'),
    path('login-telegram/', LoginFromTelegramBotTemplateView.as_view(), name='login_telegram'),
    path('login-check/', LoginCheckView.as_view(), name='login_check'),
    path('logout', LogoutView.as_view(next_page='product_list'), name='logout'),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file")
]
