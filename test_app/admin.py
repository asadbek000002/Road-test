from django.contrib import admin
from .models import Category, Question, AnswerChoice


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 2  # Sukut bo‘yicha 3 ta bo‘sh variant qo‘shiladi
    min_num = 2  # Kamida 2 ta variant bo‘lishi kerak
    max_num = 6  # Maksimal 5 ta variant qo‘shish mumkin

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
    list_display = ('text', 'category',)
    list_filter = ('category',)
    search_fields = ('text',)

    inlines = [AnswerChoiceInline]  # Inline qo‘shildi


@admin.register(Category)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at',)
    search_fields = ('title',)


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct',)
    list_filter = ('is_correct',)
    search_fields = ('text',)
