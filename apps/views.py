from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, Count, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, UpdateView, CreateView, TemplateView

from apps.forms import OrderModelForm, LoginForm, UserProfileModelForm, StreamForm
from apps.models import Product, Category, Order, User, Stream, Wishlist


class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/product/index.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.GET.get('category')
        search = self.request.POST.get('q')
        if search:
            queryset = queryset.filter(F(description__icontains=search) & F(name__icontains=search))
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'apps/product/product-detail.html'


class LoginFormView(FormView):
    template_name = 'apps/auth/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class OrderFormView(FormView):
    template_name = 'apps/product/product-detail.html'
    form_class = OrderModelForm
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class OrderListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.all()
    template_name = 'apps/product/ordered-products.html'
    context_object_name = 'orders'


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileModelForm
    template_name = 'apps/auth/user-profile.html'

    def form_valid(self, form):
        return redirect('profile', pk=self.request.user.pk)

    def get_object(self, queryset=None):
        return self.request.user


class MarketListView(LoginRequiredMixin, ListView):
    queryset = Product.objects.all()
    template_name = 'apps/product/market.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class StreamCreateView(LoginRequiredMixin, CreateView):
    model = Stream
    form_class = StreamForm
    template_name = 'apps/product/market.html'

    def form_valid(self, form):
        stream = form.save(commit=False)
        stream.user = self.request.user
        stream.save()
        return redirect('stream_list')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class StreamListView(LoginRequiredMixin, ListView):
    queryset = Stream.objects.all()
    template_name = 'apps/product/stream.html'
    context_object_name = 'streams'

    def get_queryset(self):
        return Stream.objects.annotate(
            new_count=Count('orders', filter=Q(orders__status='new')),
            visit_count=Count('orders', filter=Q(orders__status='visit')),
            ready_count=Count('orders', filter=Q(orders__status='ready')),
            delivery_count=Count('orders', filter=Q(orders__status='delivery')),
            delivered_count=Count('orders', filter=Q(orders__status='delivered')),
            cancelled_count=Count('orders', filter=Q(orders__status='cancelled')),
            archived_count=Count('orders', filter=Q(orders__status='archived')),
            missed_call_count=Count('orders', filter=Q(orders__status='missed_call'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        status_counts = queryset.aggregate(
            new_count_total=Sum('new_count'),
            visit_count_total=Sum('visit_count'),
            ready_count_total=Sum('ready_count'),
            delivery_count_total=Sum('delivery_count'),
            delivered_count_total=Sum('delivered_count'),
            cancelled_count_total=Sum('cancelled_count'),
            archived_count_total=Sum('archived_count'),
            missed_call_count_total=Sum('missed_call_count')
        )
        context.update(status_counts)
        return context


class StatisticTemplateView(TemplateView):
    template_name = 'apps/product/statistic.html'


# class AddToWishlistView(DetailView):
#     model = Wishlist
#     context_object_name = 'wishlist'
#
#     def post(self, request, *args, **kwargs):
#         if self.request.is_ajax() and self.request.POST and 'attr_id' in self.request.POST:
#             if self.request.user.is_authenticated:
#                 data = Wishlist.objects.filter(user=request.user, music_id=request.POST['attr_id'])
#                 if data.exists():
#                     data.delete()
#                 else:
#                     Wishlist.objects.create(user=request.user, music_id=request.POST['attr_id'])
#         else:
#             print("No Product is Found")
#
#         return redirect("product_list")


class WishlistListView(LoginRequiredMixin, ListView):
    queryset = Wishlist.objects.all()
    template_name = 'apps/product/wishlist.html'
    context_object_name = 'liked_products'
