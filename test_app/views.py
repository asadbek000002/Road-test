from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Question, AnswerChoice, Category
from .serializers import SubmitAnswersSerializer, QuestionSerializer, CategorySerializer, SubmitPageAnswersSerializer, \
    SubmitRandomAnswersSerializer
from django.db.models import Count


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_random_questions(request):
    """Tasodifiy 20 ta savolni qaytarish, agar `force_new` bo‘lsa yangi yaratish"""
    force_new = request.data.get("force_new", False)
    cache_key = f"random_questions_{request.user.id}"
    cache_question_ids_key = f"random_question_ids_{request.user.id}"

    if force_new or not cache.get(cache_key):
        selected_questions = list(Question.objects.order_by('?')[:20])  # Tasodifiy 20 ta olish
        question_ids = [q.id for q in selected_questions]  # Faqat ID-larni olish

        # Cache-ga savollarni va ularning ID-larini saqlash
        cache.set(cache_key, selected_questions, timeout=1800)  # 30 daqiqa
        cache.set(cache_question_ids_key, question_ids, timeout=1800)  # 30 daqiqa
    else:
        selected_questions = cache.get(cache_key)

    serializer = QuestionSerializer(selected_questions, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question_pages(request):
    """Savollarni sahifalarga ajratib, faqat sahifa raqamlarini chiqarish"""
    total_questions = Question.objects.aggregate(count=Count('id'))['count']
    page_size = 10  # Har bir sahifada 10 savol bo‘lishi
    total_pages = -(-total_questions // page_size)  # Yuqoriga yaxlitlash (ceil)

    return Response({
        "total_pages": total_pages,
        "page_numbers": list(range(1, total_pages + 1))
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questions_by_page(request, page_number):
    """Tanlangan sahifadagi savollarni chiqarish 10 tadan"""
    page_size = 10

    # Savollarni order bo‘yicha tartiblash
    questions = Question.objects.only('id', 'text', 'image', 'correct_answer', 'order') \
        .order_by('order')  # order bo‘yicha tartiblash

    # Sahifalashni qo‘shish
    questions = questions[page_size * (page_number - 1):page_size * page_number]

    serializer = QuestionSerializer(questions, many=True, context={'request': request})
    return Response({
        "current_page": page_number,
        "questions": serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questions(request):
    """Savollar va javob variantlarini `order` bo‘yicha oshish tartibida optimallashtirilgan holda olish"""
    questions = Question.objects.only('id', 'text', 'image', 'correct_answer', 'order') \
        .prefetch_related('choices') \
        .order_by('order')

    serializer = QuestionSerializer(questions, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questions_by_category(request, category_id):
    """Berilgan kategoriya ID bo‘yicha savollarni optimallashtirilgan holda olish"""
    category = get_object_or_404(Category.objects.only('id', 'title'), id=category_id)

    questions = Question.objects.filter(category=category) \
        .only('id', 'text', 'image', 'correct_answer', 'order') \
        .prefetch_related('choices') \
        .order_by('order')  # Tartib bo‘yicha oshish

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
def submit_random_answers(request):
    """Tasodifiy savollar uchun foydalanuvchi javoblarini tekshirish"""
    cache_key = f"random_question_ids_{request.user.id}"
    question_ids = cache.get(cache_key)  # Cache-dagi tasodifiy savollar IDlari

    if not question_ids:
        return Response({"error": "Test sessiyasi topilmadi. Iltimos, yangi test boshlang!"}, status=400)

    serializer = SubmitRandomAnswersSerializer(data=request.data, context={'request': request})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    answers = serializer.validated_data.get("answers", [])
    print("sahifadagi savollar", question_ids)

    # Foydalanuvchi faqat test sessiyasidagi savollarga javob berganligini tekshiramiz
    answered_question_ids = {answer["question_id"] for answer in answers}
    print("yuborilgan savollar", answered_question_ids)

    if not answered_question_ids.issubset(set(question_ids)):
        return Response({"error": "Noto‘g‘ri savol ID jo‘natildi!"}, status=400)

    # Barcha javob variantlari IDlari
    answer_ids = [answer["answer_id"] for answer in answers if answer["answer_id"] is not None]
    correct_answers = set(
        AnswerChoice.objects.filter(id__in=answer_ids, is_correct=True).values_list("id", flat=True)
    )

    # To‘g‘ri va noto‘g‘ri javoblarni sanash
    correct_count = sum(1 for answer in answers if answer["answer_id"] in correct_answers)
    total_questions = len(question_ids)
    incorrect_count = total_questions - correct_count

    percentage = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0

    # Test tugatilgandan so‘ng cache-ni o‘chiramiz
    # cache.delete(cache_key)

    return Response({
        "total_questions": total_questions,
        "correct_answers": correct_count,
        "incorrect_answers": incorrect_count,
        "percentage": percentage
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_paged_answers(request, page_number):
    """Sahifalar bo‘yicha foydalanuvchi javoblarini tekshirish"""
    serializer = SubmitPageAnswersSerializer(data=request.data, context={'page_number': page_number})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    answers = serializer.validated_data.get("answers", [])

    # Sahifaga mos savollarni olish
    page_size = 10
    questions = Question.objects.only('id', 'text', 'image', 'correct_answer').order_by('order')[
                page_size * (page_number - 1):page_size * page_number
                ]

    # Sahifadagi savollar IDlarini olish
    question_ids = {question.id for question in questions}

    # Yuborilgan savollarning IDlarini olish
    answered_question_ids = {answer["question_id"] for answer in answers}
    # Yuborilgan savollar faqat ushbu sahifaga tegishli bo‘lishi kerak
    if not answered_question_ids.issubset(question_ids):
        return Response({"error": "Berilgan savollar ushbu sahifada mavjud emas!"}, status=400)

    # To‘g‘ri va noto‘g‘ri javoblarni sanash
    correct_count = 0
    incorrect_count = 0

    # Har bir savolga javobni tekshirish
    for question_id in question_ids:
        # Savolga tegishli javobni topamiz
        answer = next((a for a in answers if a["question_id"] == question_id), None)

        if answer:
            # Javob berilgan bo'lsa, uni tekshirish
            correct_answer = AnswerChoice.objects.filter(question_id=question_id, is_correct=True).first()
            if correct_answer and answer["answer_id"] == correct_answer.id:
                correct_count += 1
            else:
                incorrect_count += 1
        else:
            # Agar javob berilmagan bo'lsa, uni noto'g'ri deb hisoblash
            incorrect_count += 1

    total_questions = len(question_ids)  # Sahifadagi savollar soni
    percentage = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0

    return Response({
        "total_questions": total_questions,  # Hozirgi sahifadagi savollar soni
        "correct_answers": correct_count,  # To‘g‘ri javoblar soni
        "incorrect_answers": incorrect_count,  # Noto‘g‘ri javoblar soni
        "percentage": percentage  # To‘g‘rilik foizi
    })
