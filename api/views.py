from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id', 'username']

class UserPasswordSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['password']

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserPasswordUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        password = request.data.get("password")
        if not password:
            return Response({"password": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(password)
        user.save()
        return Response({"detail": "Password updated successfully."})
