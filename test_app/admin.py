from django.contrib import admin
from .models import Category, Question, AnswerChoice


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 2  # Sukut bo‘yicha 3 ta bo‘sh variant qo‘shiladi
    min_num = 2  # Kamida 2 ta variant bo‘lishi kerak
    max_num = 6  # Maksimal 5 ta variant qo‘shish mumkin
    exclude = ('text',)

    def get_extra(self, request, obj=None, **kwargs):
        """
        Sukut bo‘yicha faqat 3 ta variant chiqishini ta’minlash.
        Agar mavjud variantlar bo‘lsa, yangi bo‘sh formalar qo‘shilmaydi.
        """
        if obj and obj.choices.count() > 0:
            return 0  # Agar mavjud bo‘lsa, bo‘sh variant qo‘shilmaydi
        return self.extra  # Aks holda, `extra` qiymati ishlaydi


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    # Savollarni 'order' bo'yicha tartiblash
    list_display = ('text_uz', 'order', 'text_ru', 'text_en', 'category')

    # Savollarni 'order' bo'yicha avtomatik tartiblash
    ordering = ['order']

    # Admin panelda 'order' ni tahrirlash imkonini yaratish
    list_editable = ['order']

    # Filtrlash
    list_filter = ('category',)

    # Qidiruv uchun so'zlar
    search_fields = ('text_uz', 'text_ru', 'text_en')

    # Inline modeli
    inlines = [AnswerChoiceInline]

    # 'text' va 'correct_answer' maydonlarini admin paneldan chiqarish
    exclude = ('text', 'correct_answer')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'title_ru', 'title_en', 'created_at',)
    search_fields = ('title_uz', 'title_ru', 'title_en')
    exclude = ('title',)  # Asl `title` maydonini yashiramiz


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = ('text_uz', 'text_ru', 'text_en', 'question', 'is_correct',)
    list_filter = ('is_correct',)
    search_fields = ('text_uz', 'text_ru', 'text_en')
    exclude = ('text',)  # Asl `text` maydonini yashiramiz
