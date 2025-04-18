from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path
from .models import (
    User, Event, Tag, Ticket, Payment, Review, DiscountCode, Notification,
    ChatMessage, EventTrendingLog
)


# Form tùy chỉnh cho Event
class EventForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget, required=False)

    class Meta:
        model = Event
        fields = '__all__'


# Form tùy chỉnh cho Notification
class NotificationForm(forms.ModelForm):
    message = forms.CharField(widget=CKEditorUploadingWidget, required=False)

    class Meta:
        model = Notification
        fields = '__all__'


# Form tùy chỉnh cho ChatMessage
class ChatMessageForm(forms.ModelForm):
    message = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = ChatMessage
        fields = '__all__'


# Admin cho User
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'role', 'total_spent', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone']
    list_filter = ['role', 'is_active', 'created_at']
    list_editable = ['role', 'is_active']
    readonly_fields = ['avatar_view']

    def avatar_view(self, user):
        if user.avatar:
            return mark_safe(f"<img src='{user.avatar.url}' width='200' />")
        return "Không có ảnh đại diện"


# Admin cho Event
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'start_time', 'organizer', 'is_active', 'total_tickets']
    search_fields = ['title', 'description', 'location']
    list_filter = ['category', 'is_active', 'start_time']
    list_editable = ['is_active']
    readonly_fields = ['poster_view']
    form = EventForm

    def poster_view(self, event):
        if event.poster:
            return mark_safe(f"<img src='{event.poster.url}' width='200' />")
        return "Không có poster"

    class Media:
        css = {
            'all': ('/static/css/admin_styles.css',)
        }


# Admin cho Tag
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


# Admin cho Ticket
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'user', 'qr_code', 'is_paid', 'is_checked_in', 'created_at']
    search_fields = ['event__title', 'user__username', 'qr_code']
    list_filter = ['is_paid', 'is_checked_in', 'created_at']
    list_editable = ['is_paid', 'is_checked_in']


# Admin cho Payment
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'payment_method', 'status', 'paid_at']
    search_fields = ['user__username', 'transaction_id']
    list_filter = ['payment_method', 'status', 'paid_at']
    readonly_fields = ['transaction_id']


# Admin cho Review
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'user', 'rating', 'comment', 'created_at']
    search_fields = ['event__title', 'user__username', 'comment']
    list_filter = ['rating', 'created_at']


# Admin cho DiscountCode
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'discount_percentage', 'user_group', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    list_filter = ['user_group', 'is_active', 'valid_from', 'valid_to']
    list_editable = ['is_active']


# Admin cho Notification
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    list_filter = ['notification_type', 'is_read', 'created_at']
    form = NotificationForm


# Admin cho ChatMessage
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'sender', 'receiver', 'message_preview', 'is_from_organizer', 'created_at']
    search_fields = ['message', 'sender__username', 'receiver__username', 'event__title']
    list_filter = ['is_from_organizer', 'created_at']
    form = ChatMessageForm

    def message_preview(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')


# Admin cho EventTrendingLog
class EventTrendingLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'view_count', 'ticket_sold_count', 'last_updated']
    search_fields = ['event__title']
    list_filter = ['last_updated']


# Custom Admin Site
class MyAdminSite(admin.AdminSite):
    site_header = 'Hệ Thống Quản Lý Sự Kiện'
    site_title = 'Quản Trị Sự Kiện'
    index_title = 'Chào Mừng Đến Với Trang Quản Trị Sự Kiện'

    def get_urls(self):
        return [
            path('event-stats/', self.event_stats, name='event-stats'),
        ] + super().get_urls()

    def event_stats(self, request):
        # Thống kê số lượng sự kiện theo danh mục
        event_stats = Event.objects.values('category').annotate(event_count=Count('id')).order_by('category')
        # Thống kê số lượng vé đã bán theo sự kiện
        ticket_stats = Event.objects.annotate(ticket_count=Count('sold_tickets')).values('title', 'ticket_count')
        # Thống kê lượt xem và vé bán theo xu hướng
        trending_stats = EventTrendingLog.objects.values('event__title', 'view_count', 'ticket_sold_count')

        return TemplateResponse(request, 'admin/event_stats.html', {
            'event_stats': event_stats,
            'ticket_stats': ticket_stats,
            'trending_stats': trending_stats,
        })


# Khởi tạo admin site
admin_site = MyAdminSite(name='event_admin')


# Đăng ký các model
admin_site.register(User, UserAdmin)
admin_site.register(Event, EventAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(Ticket, TicketAdmin)
admin_site.register(Payment, PaymentAdmin)
admin_site.register(Review, ReviewAdmin)
admin_site.register(DiscountCode, DiscountCodeAdmin)
admin_site.register(Notification, NotificationAdmin)
admin_site.register(ChatMessage, ChatMessageAdmin)
admin_site.register(EventTrendingLog, EventTrendingLogAdmin)