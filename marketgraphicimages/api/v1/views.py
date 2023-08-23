from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views import View
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

User = get_user_model()


class RedirectSocial(View):

    def get(self, request, *args, **kwargs):
        code, state = str(request.GET['code']), str(request.GET['state'])
        json_obj = {'code': code, 'state': state}
        return JsonResponse(json_obj)


class UserViewSet(UserViewSet):
    """Update reset_password method logic.
    The method sends a six-digit confirmation code to the user's email.
    Added reset_password_confirm_code method. It checks the confirmation code.
    Update reset_password_confirm method. This method changes the password
    after successful confirmation of the code.
    """
    def get_permissions(self):
        if self.action == 'reset_password_confirm_code':
            self.permission_classes = (
                settings.PERMISSIONS.password_reset_confirm_code
            )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'reset_password_confirm_code':
            return settings.SERIALIZERS.password_reset_confirm_code
        return super().get_serializer_class()

    @action(['post'], detail=False)
    def reset_password_confirm_code(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            is_token_valid = serializer.validated_data.get('user_confirm_code')
            is_token_valid.is_confirmed = True
            is_token_valid.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(['post'], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        user.set_password(serializer.validated_data.get('new_password'))
        user.code_owner.all().delete()
        user.save()
        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {'user': user}
            to = [serializer.validated_data.get('email')]
            settings.EMAIL.password_changed_confirmation(
                self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)
