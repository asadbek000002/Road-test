from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Contact


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'username', 'is_active')  # is_active mavjud
    list_filter = ('is_active',)
    search_fields = ('phone_number', 'username')

    readonly_fields = ('password',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'username', 'is_active', 'is_staff', 'is_superuser')}),
    )

    list_editable = ('is_active',)  # ✅ Endi admin panelda is_active ni to‘g‘ridan-to‘g‘ri tahrirlash mumkin



from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Faqat bitta obyekt bo'lsa, qo'shish imkonini bermaydi
        return not Contact.objects.exists()

    def get_queryset(self, request):
        # Har doim barcha obyektlarni chiqarish
        return super().get_queryset(request)

    list_display = ('tg_link', 'card_number')

