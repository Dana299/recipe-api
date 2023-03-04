from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.jwt_auth import set_jwt_cookies, unset_jwt_cookies
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .serializers import CustomRegisterSerialiazer, CustomUserDetailsSerializer


class UserCreateView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = CustomRegisterSerialiazer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            if new_user:
                return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CookieBasedRegisterView(RegisterView):
    """
    Register view for setting both access
    and refresh tokens in cookies.
    """
    serializer_class = CustomRegisterSerialiazer

    def get_response_data(self, user):

        data = {'user': user, }

        return CustomUserDetailsSerializer(
            data,
            context=self.get_serializer_context()
        ).data

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        set_jwt_cookies(response, self.access_token, self.refresh_token)
        return response


class CookieBasedLogoutView(LogoutView):
    """
    Logout view that logs out the user when BOTH access
    and refresh token are put into httpOnly cookies
    """
    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        response = Response(
            {'detail': _('Successfully logged out.')},
            status=status.HTTP_200_OK,
        )

        access_cookie_name = settings.REST_AUTH['JWT_AUTH_COOKIE']
        refresh_cookie_name = settings.REST_AUTH['JWT_AUTH_REFRESH_COOKIE']

        try:
            token = AccessToken(request.COOKIES[access_cookie_name])
        except KeyError:
            response.data = {'detail': _('Access token cookies were not provided.')}
            response.status_code = status.HTTP_401_UNAUTHORIZED

        try:
            token = RefreshToken(request.COOKIES[refresh_cookie_name])
            token.blacklist()
        except KeyError:
            response.data = {'detail': _('Refresh token cookies were not provided.')}
            response.status_code = status.HTTP_401_UNAUTHORIZED

        except (TokenError, AttributeError, TypeError) as error:
            if hasattr(error, 'args'):
                if 'Token is blacklisted' in error.args or 'Token is invalid or expired' in error.args:
                    response.data = {'detail': _(error.args[0])}
                    response.status_code = status.HTTP_401_UNAUTHORIZED
                else:
                    response.data = {'detail': _('An error has occurred.')}
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            else:
                response.data = {'detail': _('An error has occurred.')}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        unset_jwt_cookies(response)

        # case when request has neither access nor refresh cookies
        if not (access_cookie_name and refresh_cookie_name):
            message = _(
                'Neither cookies or blacklist are enabled, so the token '
                'has not been deleted server side. Please make sure the token is deleted client side.',
            )
            response.data = {'detail': message}
            response.status_code = status.HTTP_200_OK
        return response


class CustomLoginView(LoginView):
    """
    Login View where get_response method was redefined.
    Allows to send refresh token if http_only = True
    and does not allow to send access token,
    not vice versa as in parent LoginView class
    """

    def get_response(self):
        serializer_class = CustomUserDetailsSerializer

        if api_settings.USE_JWT:

            data = {
                'user': self.user,
            }

            serializer = serializer_class(
                instance=data,
                context=self.get_serializer_context(),
            )

        elif self.token:
            serializer = serializer_class(
                instance=self.token,
                context=self.get_serializer_context(),
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

        response = Response(serializer.data, status=status.HTTP_200_OK)

        # set access token cookies
        set_jwt_cookies(response, self.access_token, self.refresh_token)
        return response
