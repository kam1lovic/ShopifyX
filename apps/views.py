from datetime import timedelta
from time import timezone

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import F, Count, Q
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, FormView, UpdateView, CreateView, TemplateView
from django.views.generic import ListView

from apps.forms import OrderModelForm, LoginForm, UserProfileModelForm, StreamForm, \
    UserPasswordModelForm, UserProfileImageModelForm, PaymentForm
from apps.models import Product, Category, Order, User, Stream, Wishlist, SiteSettings, Competition, Payment


class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/product/index.html'
    context_object_name = 'products'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        site_settings = SiteSettings.objects.first()
        if site_settings:
            context['delivery_price'] = site_settings.delivery_cost
        else:
            context['delivery_price'] = 0

        context['selected_category_slug'] = self.request.GET.get('category', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'apps/product/product-detail.html'
    context_object_name = 'product'

    def get_current_obj(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)

        if pk is not None:
            stream = get_object_or_404(Stream.objects.all(), pk=pk)
            stream.count += 1
            stream.save()
            return stream.product, stream

        product = get_object_or_404(Product.objects.all(), slug=slug)
        return product, None

    def get_object(self, queryset=None):
        product, _ = self.get_current_obj()
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stream_id'] = self.kwargs.get(self.pk_url_kwarg, '')
        product, stream = self.get_current_obj()

        if stream:
            price = stream.product.price  # Initialize price with the product's base price
            if stream.benefit:
                price += stream.benefit
            if stream.discount:
                price -= stream.discount
        else:
            price = product.price  # Initialize price with the product's base price

        context['price'] = price
        return context


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
    success_url = reverse_lazy('success_order')

    def form_valid(self, form):
        order = form.save(False)
        if order.stream:
            order.referral_user = order.stream.owner
            order.save()
        order.user = self.request.user
        order.save()
        return redirect(reverse_lazy('success_order', kwargs={'pk': order.pk}))


class OrderListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.all()
    template_name = 'apps/product/ordered-products.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.annotate(
            total_price=Sum(F('product__price') * F('quantity'))
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context.update(**qs.aggregate(
            total_p=Sum('total_price')
        ))
        return context


class SuccessOrderTemplateView(TemplateView):
    template_name = 'apps/product/success_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('pk')
        self.order = get_object_or_404(Order, pk=order_id)

        context['order'] = self.order
        context['product'] = self.order.product
        context['total_price'] = self.order.quantity * self.order.product.price

        site_settings = SiteSettings.objects.first()
        if site_settings:
            context['delivery_price'] = site_settings.delivery_cost
        else:
            context['delivery_price'] = 0

        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileModelForm
    template_name = 'apps/auth/user-profile.html'

    def form_valid(self, form):
        form.save()
        return redirect('profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserProfileImageUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileImageModelForm
    template_name = 'apps/auth/user-profile.html'

    def form_valid(self, form):
        form.save()
        return redirect('profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserChangePasswordFormView(FormView):
    template_name = 'apps/auth/user-profile.html'
    form_class = UserPasswordModelForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = self.request.user
        old_password = form.cleaned_data['password']
        new_password = form.cleaned_data['new_password1']
        confirm_new_password = form.cleaned_data['new_password2']

        if user.check_password(old_password):
            if new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()
                messages.success(self.request, 'Parol muvaffaqiyatli o\'zgartirildi.')
            else:
                messages.error(self.request, 'Yangi parol va yangi parolni takrorlash mos kelmadi.')
                return self.form_invalid(form)
        else:
            messages.error(self.request, 'Oldingi parol noto\'g\'ri.')
            return self.form_invalid(form)

        update_session_auth_hash(self.request, user)
        return redirect('profile')


class MarketListView(LoginRequiredMixin, ListView):
    queryset = Product.objects.all()
    template_name = 'apps/product/market.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.GET.get('category')
        if category_slug == 'top_product':
            queryset = self.get_top_products()
        elif category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_top_products(self):
        today = timezone.now()
        last_week = today - timedelta(days=7)
        qs = Order.objects.filter(created_at__gte=last_week, status=Order.Status.DELIVERED)
        top_products = qs.values('product__id').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
        product_ids = [item['product__id'] for item in top_products]
        return Product.objects.filter(id__in=product_ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category_slug'] = self.request.GET.get('category')
        return context


class StreamCreateView(LoginRequiredMixin, CreateView):
    model = Stream
    form_class = StreamForm
    template_name = 'apps/product/market.html'

    def form_valid(self, form):
        stream = form.save(commit=False)
        stream.owner = self.request.user

        if stream.discount and stream.product.user_payment < stream.discount:
            messages.error(self.request, 'Oqim chegirmasi mahsulot toʻlovi summasidan katta boʻlishi mumkin emas.')
            return redirect('market_list')

        stream.save()
        messages.success(self.request, 'Oqim muvaffaqqiyatli yaratildi!')
        return redirect('market_list')

    def form_invalid(self, form):
        messages.error(self.request, 'Oqim yaratishda xatolik yuz berdi. Oqimni tuzatib, qaytadan urinib ko‘ring.')
        return self.render_to_response(self.get_context_data(form=form))


class StreamListView(LoginRequiredMixin, ListView):
    queryset = Stream.objects.all().order_by('-id')
    template_name = 'apps/product/stream.html'
    context_object_name = 'streams'


class StatisticListView(ListView):
    queryset = Stream.objects.all()
    template_name = 'apps/product/statistic.html'
    context_object_name = 'streams'

    def get_period_filter(self):
        period = self.request.GET.get('period', 'today')
        now = timezone.now()
        end_date = None
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'last_day':
            start_date = now - timedelta(days=1)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'weekly':
            start_date = now - timedelta(days=now.weekday())
        elif period == 'monthly':
            start_date = now.replace(day=1)
        elif period == 'all':
            start_date = None
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        return start_date, end_date

    def get_queryset(self):
        qs = super().get_queryset()
        start_date, end_date = self.get_period_filter()

        if start_date:
            if end_date:
                qs = qs.filter(orders__created_at__range=(start_date, end_date))
            else:
                qs = qs.filter(orders__created_at__gte=start_date)

        return qs.annotate(
            new_count=Count('orders', filter=Q(orders__status=Order.Status.NEW)),
            visit_count=Count('orders', filter=Q(orders__status=Order.Status.VISIT)),
            ready_count=Count('orders', filter=Q(orders__status=Order.Status.READY)),
            delivery_count=Count('orders', filter=Q(orders__status=Order.Status.DELIVERY)),
            delivered_count=Count('orders', filter=Q(orders__status=Order.Status.DELIVERED)),
            cancelled_count=Count('orders', filter=Q(orders__status=Order.Status.CANCELLED)),
            archived_count=Count('orders', filter=Q(orders__status=Order.Status.ARCHIVED)),
            missed_call_count=Count('orders', filter=Q(orders__status=Order.Status.MISSED_CALL))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context.update(**qs.aggregate(
            new_count_total=Sum('new_count'),
            visit_count_total=Sum('visit_count'),
            ready_count_total=Sum('ready_count'),
            delivery_count_total=Sum('delivery_count'),
            delivered_count_total=Sum('delivered_count'),
            cancelled_count_total=Sum('cancelled_count'),
            archived_count_total=Sum('archived_count'),
            missed_call_count_total=Sum('missed_call_count'),
        ))

        context['selected_period'] = self.request.GET.get('period', 'today')
        return context


class WishlistView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product_slug = kwargs['product_slug']
        product = get_object_or_404(Product, slug=product_slug)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            wishlist.delete()
        return redirect('/')


class RemoveFromWishlistView(View):
    def get(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        Wishlist.objects.filter(product=product, user=request.user).delete()
        return redirect('wishlist')


class WishlistListView(LoginRequiredMixin, ListView):
    queryset = Wishlist.objects.all()
    template_name = 'apps/product/wishlist.html'
    context_object_name = 'wishlists'


class OperatorTemplateView(TemplateView):
    template_name = 'apps/operator/operator.html'


class CompetitionListView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/competition/competition.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_competition = Competition.objects.filter(is_active=True).first()

        if active_competition:
            orders = (
                Order.objects.filter(
                    created_at__gte=active_competition.start_date, status=Order.Status.DELIVERED
                ).values(
                    'referral_user__first_name', 'quantity'
                ).annotate(order_count=Sum('quantity')).order_by('-order_count')
            )
            context['stream_winfo'] = orders
            context['competition'] = active_competition
        else:
            context['stream_winfo'] = []
            context['competition'] = None

        return context


class LoginFromTelegramBotTemplateView(TemplateView):
    template_name = 'apps/auth/login_with_tlg_bot.html'


class LoginCheckView(View):
    def post(self, request, *args, **kwargs):
        code = request.POST.get('code', '')
        if len(code) != 6:
            return JsonResponse({'msg': 'error code'}, status=400)
        phone = cache.get(code)
        if phone is None:
            return JsonResponse({'msg': 'expired code'}, status=400)
        user = User.objects.get(phone_number=phone)
        login(request, user)
        return JsonResponse({'msg': 'OK'})


class DiagramTemplateView(TemplateView):
    template_name = 'apps/diagrams/diagrams.html'


class PaymentFormView(LoginRequiredMixin, FormView):
    template_name = 'apps/payment/payment.html'
    form_class = PaymentForm
    success_url = reverse_lazy('payment_info')

    def form_valid(self, form):
        user: User = self.request.user
        amount = form.cleaned_data.get('amount')
        MIN_AMOUNT = 150000

        if amount < MIN_AMOUNT:
            messages.error(self.request, f"Amount must be at least {MIN_AMOUNT}.")
            return redirect(self.success_url)

        if amount > user.balance:
            messages.error(self.request, "Amount cannot be greater than your current balance.")
            return redirect(self.success_url)

        user.balance -= amount
        user.save()

        payment = form.save(commit=False)
        payment.user = self.request.user
        payment.save()
        messages.success(self.request, "Payment request submitted successfully.")
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)



class PaymentInfoListView(LoginRequiredMixin, ListView):
    queryset = Payment.objects.all()
    template_name = 'apps/payment/payment.html'
    context_object_name = 'payment_info'

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
