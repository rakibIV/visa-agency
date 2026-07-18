from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

from rest_framework import serializers

class UserProfileSerializer(ModelSerializer):
    smtp_email = serializers.CharField(source='staff_profile.smtp_email', allow_blank=True, required=False)
    smtp_password = serializers.CharField(source='staff_profile.smtp_password', allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'smtp_email', 'smtp_password']
        read_only_fields = ['id', 'username']

    def update(self, instance, validated_data):
        staff_data = validated_data.pop('staff_profile', None)
        instance = super().update(instance, validated_data)
        
        if staff_data is not None:
            if not hasattr(instance, 'staff_profile') and instance.is_superuser:
                from staff.models import Staff, Designation
                from staff.utils import _generate_employee_id
                from agency.models import Office, CompanyInformation
                import datetime
                designation, _ = Designation.objects.get_or_create(name='System Admin')
                company, _ = CompanyInformation.objects.get_or_create(company_name='Default Company')
                office, _ = Office.objects.get_or_create(company=company, branch_name='Head Office', defaults={'phone': '0000', 'address': 'Default'})
                Staff.objects.create(
                    user=instance,
                    employee_id=_generate_employee_id(),
                    designation=designation,
                    office=office,
                    joining_date=datetime.date.today(),
                    date_of_birth=datetime.date(1990, 1, 1),
                    gender='male',
                    nationality='Default',
                    phone='00000000',
                    father_name='System',
                    mother_name='Admin',
                    smtp_email=staff_data.get('smtp_email', ''),
                    smtp_password=staff_data.get('smtp_password', '')
                )
            elif hasattr(instance, 'staff_profile'):
                instance.staff_profile.smtp_email = staff_data.get('smtp_email', instance.staff_profile.smtp_email)
                instance.staff_profile.smtp_password = staff_data.get('smtp_password', instance.staff_profile.smtp_password)
                instance.staff_profile.save()
            
        return instance

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
