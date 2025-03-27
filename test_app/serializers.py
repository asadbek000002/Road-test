from rest_framework import serializers
from django.utils.translation import get_language
from .models import AnswerChoice, Question, Category


class CategorySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title']  # Faqat dinamik title

    def get_title(self, obj):
        lang = get_language()  # Foydalanuvchining hozirgi tili
        return getattr(obj, f"title_{lang}", obj.title_uz)  # Agar title_{lang} bo‘lmasa, default "uz"


# savollarni get qilish

class AnswerChoiceSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()  # Dinamik text qo‘shildi

    class Meta:
        model = AnswerChoice
        fields = ['id', 'text', 'is_correct']  # `is_correct` ham qo'shildi

    def get_text(self, obj):
        lang = get_language()  # Joriy foydalanuvchi tili
        return getattr(obj, f"text_{lang}", obj.text_uz)  # Standart `uz` bo‘ladi


class QuestionSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()  # Dinamik text
    correct_answer = serializers.SerializerMethodField()  # Dinamik javob
    choices = AnswerChoiceSerializer(many=True, read_only=True)  # Tanlov variantlari

    class Meta:
        model = Question
        fields = ['id', 'text', 'image', 'correct_answer', 'choices']

    def get_text(self, obj):
        lang = get_language()  # Joriy tilni olish
        return getattr(obj, f"text_{lang}", obj.text_uz)  # Agar mavjud bo‘lmasa, `uz`

    def get_correct_answer(self, obj):
        lang = get_language()  # Joriy til
        return getattr(obj, f"correct_answer_{lang}", obj.correct_answer_uz)  # Agar mavjud bo‘lmasa, `uz`


# userni javoblarini olish
class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()

    def validate(self, data):
        """
        Foydalanuvchining tanlagan javobining haqiqiyligini tekshirish
        """
        question_id = data.get("question_id")
        answer_id = data.get("answer_id")

        # Savol mavjudligini tekshirish
        if not Question.objects.filter(id=question_id).exists():
            raise serializers.ValidationError({"question_id": "Bunday savol topilmadi."})

        # Variant mavjudligini tekshirish
        if not AnswerChoice.objects.filter(id=answer_id, question_id=question_id).exists():
            raise serializers.ValidationError({"answer_id": "Tanlangan variant ushbu savolga tegishli emas."})

        return data


class SubmitAnswersSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=AnswerSerializer(),
        required=False,  # Majburiy emas
        allow_empty=True  # Bo‘sh bo‘lishiga ruxsat berish
    )

    def validate(self, data):
        """Foydalanuvchining jo‘natgan javoblarini tekshirish"""
        answers = data.get("answers", [])

        # Barcha savollarni olish
        all_question_ids = set(Question.objects.values_list("id", flat=True))
        answered_question_ids = {answer["question_id"] for answer in answers}

        # Agar foydalanuvchi ba’zi savollarga javob bermagan bo‘lsa, ularni noto‘g‘ri hisoblash uchun qo‘shamiz
        missing_questions = all_question_ids - answered_question_ids
        for question_id in missing_questions:
            answers.append({"question_id": question_id, "answer_id": None})  # Hech qanday javob berilmagan

        data["answers"] = answers
        return data
