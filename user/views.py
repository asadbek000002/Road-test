from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from rest_framework.views import APIView
from .models import Contact
from .serializers import ContactSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']

        # JWT token yaratamiz
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")  # Foydalanuvchi yuborgan refresh token
        if not refresh_token:
            return Response({"error": "Refresh token talab qilinadi!"}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()  # Tokenni blacklistga qo‘shamiz

        return Response({"message": "Tizimdan chiqildi."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Xatolik yuz berdi!"}, status=status.HTTP_400_BAD_REQUEST)


class ContactAPIView(APIView):
    def get(self, request):
        contact = Contact.objects.first()  # Faqat bitta obyektni qaytaradi
        if contact:
            serializer = ContactSerializer(contact)
            return Response(serializer.data)
        return Response({"message": "Contact not found"}, status=404)
