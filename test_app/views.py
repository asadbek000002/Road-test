from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Question, AnswerChoice, Category
from .serializers import SubmitAnswersSerializer, QuestionSerializer, CategorySerializer
from django.db.models import Count


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_random_questions(request):
    """Tasodifiy 20 ta savolni qaytarish, agar `force_new` bo‘lsa yangi yaratish"""
    force_new = request.data.get("force_new", False)
    cache_key = f"random_questions_{request.user.id}"

    if force_new or not cache.get(cache_key):
        selected_questions = list(Question.objects.order_by('?')[:20])  # DB dan tasodifiy 20 ta olish
        cache.set(cache_key, selected_questions, timeout=300)  # 5 daqiqa kesh
    else:
        selected_questions = cache.get(cache_key)

    serializer = QuestionSerializer(selected_questions, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question_pages(request):
    """Savollarni sahifalarga ajratib, faqat sahifa raqamlarini chiqarish"""
    total_questions = Question.objects.aggregate(count=Count('id'))['count']
    page_size = 20  # Har bir sahifada nechta savol bo‘lishi
    total_pages = -(-total_questions // page_size)  # Yuqoriga yaxlitlash (ceil)

    return Response({
        "total_pages": total_pages,
        "page_numbers": list(range(1, total_pages + 1))
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questions_by_page(request, page_number):
    """Tanlangan sahifadagi 20 ta savolni chiqarish"""
    page_size = 20
    questions = Question.objects.only('id', 'text', 'image', 'correct_answer')[
                page_size * (page_number - 1):page_size * page_number]

    serializer = QuestionSerializer(questions, many=True, context={'request': request})
    return Response({
        "current_page": page_number,
        "questions": serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questions(request):
    """Savollar va javob variantlarini optimallashtirilgan holda olish"""
    questions = Question.objects.only('id', 'text', 'image', 'correct_answer').prefetch_related('choices')

    serializer = QuestionSerializer(questions, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questions_by_category(request, category_id):
    """Berilgan kategoriya ID bo‘yicha savollarni optimallashtirilgan holda olish"""
    category = get_object_or_404(Category.objects.only('id', 'title'), id=category_id)

    questions = Question.objects.filter(category=category).only('id', 'text', 'image',
                                                                'correct_answer').prefetch_related('choices')

    serializer = QuestionSerializer(questions, many=True, context={'request': request})
    return Response({
        "category": category.title,
        "questions": serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_categories(request):
    """Barcha kategoriyalarni optimallashtirilgan holda olish"""
    categories = Category.objects.only('id', 'title')  # Faqat kerakli maydonlarni olish
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answers(request):
    """Foydalanuvchi javoblarini tekshirib natijani qaytarish"""
    serializer = SubmitAnswersSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    answers = serializer.validated_data.get("answers", [])

    # Barcha javob variantlari IDlari
    answer_ids = [answer["answer_id"] for answer in answers if answer["answer_id"] is not None]
    correct_answers = set(
        AnswerChoice.objects.filter(id__in=answer_ids, is_correct=True).values_list("id", flat=True)
    )

    # To‘g‘ri va noto‘g‘ri javoblarni sanash
    correct_count = sum(1 for answer in answers if answer["answer_id"] in correct_answers)
    total_questions = len(answers)
    incorrect_count = total_questions - correct_count  # Noto‘g‘ri hisoblanganlar

    percentage = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0

    return Response({
        "total_questions": total_questions,
        "correct_answers": correct_count,
        "incorrect_answers": incorrect_count,
        "percentage": percentage
    })
