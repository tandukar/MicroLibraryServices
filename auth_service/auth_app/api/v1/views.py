from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomUserSerializer, LoginSerializer
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

from auth_app.tasks import send_otp_email
from auth_app.models import CustomUser
from auth_app.utlis import *
from auth_app.signals import send_mail


class RegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "User created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            access_token = serializer.validated_data["access_token"]
            refresh_token = serializer.validated_data["refresh_token"]
            mfa = serializer.validated_data["2fa"]
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]

            if mfa:
                # 2FA is enabled, return message about OTP verification
                return self.get_2fa_response(mfa, email, otp)
            else:
                # Set cookies only if 2FA is not enabled
                return self.get_cookie_response(access_token, refresh_token, mfa)

        except Exception as e:
            return Response(
                {"success": False, "error": "An error occurred during login."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_2fa_response(self, mfa, email, otp):
        send_otp_email.delay(email, otp)
        return Response(
            {
                "success": True,
                "message": "User Logged in successfully. OTP verification required.",
                "data": {"access_token": None, "refresh_token": None, "2fa": mfa},
            },
            status=status.HTTP_201_CREATED,
        )

    def get_cookie_response(self, access_token, refresh_token, mfa):
        response = Response(
            {
                "success": True,
                "message": "User Logged in successfully",
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "2fa": mfa,
                },
            },
            status=status.HTTP_201_CREATED,
        )

        response.set_cookie("access_token", access_token, httponly=True)
        response.set_cookie("refresh_token", refresh_token, httponly=True)

        return response


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        user = CustomUser.objects.filter(email=email).first()

        if user.otp == otp:
            user.otp = None
            user.save()

            access_token, refresh_token = generate_tokens(user)

            response = Response(
                {
                    "success": True,
                    "message": "User Logged in successfully",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

            response.set_cookie("access_token", access_token, httponly=True)
            response.set_cookie("refresh_token", refresh_token, httponly=True)

            return response

        return Response(
            {"success": False, "message": "Invalid OTP"},
            status=status.HTTP_400_BAD_REQUEST,
        )
