from modeltranslation.translator import register, TranslationOptions
from .models import Category, Question, AnswerChoice


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ('text', 'correct_answer')


@register(AnswerChoice)
class AnswerChoiceTranslationOptions(TranslationOptions):
    fields = ('text',)
