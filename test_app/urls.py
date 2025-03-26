from django.urls import path
from .views import submit_answers, get_questions, get_random_questions, \
    get_questions_by_category, get_categories, get_question_pages, get_questions_by_page

urlpatterns = [

    path('random-questions/', get_random_questions, name="test-get"),
    path('questions/pages/', get_question_pages, name='get_question_pages'),
    path('questions/page/<int:page_number>/', get_questions_by_page, name='get_questions_by_page'),
    path('all-questions/', get_questions, name="all-questions"),
    path('categories/', get_categories, name='categories-list'),
    path('categories/<int:category_id>/questions/', get_questions_by_category, name="categories-questions"),

    path('submit-answers/', submit_answers, name="submit_answers"),
]
