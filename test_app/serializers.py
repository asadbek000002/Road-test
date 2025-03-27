from rest_framework import serializers
from .models import AnswerChoice, Question, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


# savollarni get qilish
class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ['id', 'text', 'is_correct']  # `is_correct` ham qo'shildi


class QuestionSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'image', 'correct_answer', 'choices']


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
