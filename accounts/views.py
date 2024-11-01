import magic
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.forms import UserRegisterForm, UserLoginForm, UserUpdateForm, PasswordUpdateForm, AIDocsUploaderForm
from accounts.serializers import LoginSerializer, UserSerializer, UserRegisterSerializer, UserUpdateSerializer, \
    PasswordUpdateSerializer, UserQuerySerializer
from vect_db import user_chat_ai, vec_db_data_transfer


# Register view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            # Display all form errors in the error message
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# Login view
def login_template(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticate the user
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                messages.success(request, 'Logged in successfully.')
                return redirect('gen_ai_chat')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserLoginForm()

    return render(request, 'registration/login.html', {'form': form})


# User profile update view
@login_required
def user_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('gen_ai_chat')
        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'registration/user_update.html', {'form': form})


# Password update view
@login_required
def update_password(request):
    if request.method == 'POST':
        form = PasswordUpdateForm(request.POST)
        if form.is_valid():
            user = request.user
            pre_password = form.cleaned_data['password']
            new_password = form.cleaned_data['password1']
            confirm_password = form.cleaned_data['password2']

            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return redirect('update_password')

            # Check if the old password is correct
            if not user.check_password(pre_password):
                messages.error(request, 'Your current password is incorrect.')
                return redirect('update_password')

            # Set the new password and update the session
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')

            return redirect('gen_ai_chat')  # Redirect to a secure page after password change
        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PasswordUpdateForm()

    return render(request, 'registration/update_password.html', {'form': form})


def user_logout(request):
    return render(request, 'registration/logout.html')


# form.cleaned_data['docs_file'].read()
# form.cleaned_data['docs_file'].name

@login_required
def gen_ai_chat_docs_upload(request):
    if request.method == 'POST':
        form = AIDocsUploaderForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['docs_file']
            file_name = file.name
            file_content = file.read()

            # Get MIME type from the file content
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(file_content)

            # Validate the file based on extension, size, and MIME type
            if file_name.endswith('.txt') and file.size <= 12 * 1024 and file_type == 'text/plain':
                data_send_to_db = vec_db_data_transfer(file_name, file_content)
                if data_send_to_db:
                    messages.success(request, 'Your document has been successfully uploaded.')
                    return redirect('aiai_doc_upload')
                messages.error(request, 'There was an issue uploading your document.')
                return redirect('ai_doc_upload')
            else:
                messages.error(request, 'Your file must be a .txt file, under 12 KB, and plain text.')
                return redirect('ai_doc_upload')

        messages.error(request, 'Please correct the errors below.')
        return redirect('ai_doc_upload')

    form = AIDocsUploaderForm()
    return render(request, 'registration/ai_file_upload.html', {'form': form})


class LoginViewAPI(APIView):
    permission_classes = [AllowAny]  # Make this open to allow users to log in

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            201: openapi.Response(
                description="Registration successful",
                examples={
                    "application/json": {"message": "Registration successful! You can now log in."}
                }
            ),
            400: "Validation errors in request"
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        return Response(UserSerializer(user).data)


class RegisterAPIView(APIView):
    @swagger_auto_schema(
        request_body=UserRegisterSerializer,
        responses={
            201: openapi.Response(
                description="Registration successful",
                examples={
                    "application/json": {"message": "Registration successful! You can now log in."}
                }
            ),
            400: "Validation errors in request"
        }
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful! You can now log in."}, status=status.HTTP_201_CREATED)

        # Collect all errors and send them in the response
        error_messages = {field: error for field, error in serializer.errors.items()}
        return Response({"errors": error_messages}, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Return the current user's profile data
        serializer = UserUpdateSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=UserUpdateSerializer,
        responses={
            201: openapi.Response(
                description="Profile Updated",
                examples={
                    "application/json": {"message": "Your profile has been updated."}
                }
            ),
            400: "Validation errors in request"
        }
    )
    def put(self, request):
        # Update the user's profile data
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)

        # Collect all errors and send them in the response
        error_messages = {field: error for field, error in serializer.errors.items()}
        return Response({"errors": error_messages}, status=status.HTTP_400_BAD_REQUEST)


class PasswordUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=PasswordUpdateSerializer,
        responses={
            201: openapi.Response(
                description="Password updated",
                examples={
                    "application/json": {"message": "Password updated successfully."}
                }
            ),
            400: "Validation errors in request"
        }
    )
    def put(self, request):
        serializer = PasswordUpdateSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['password1']

            # Set the new password
            user.set_password(new_password)
            user.save()

            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            return Response({"message": "Your password was successfully updated!"}, status=status.HTTP_200_OK)

        # Return errors if any
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserAIChatView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserQuerySerializer,
        responses={
            201: openapi.Response(
                description="AI Chat",
                examples={
                    "application/json": {"message": "Conversation with AI."}
                }
            ),
            400: "Validation errors in request"
        }
    )
    def post(self, request):
        serializer = UserQuerySerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data['user_query']
            gen_ai_response = user_chat_ai(message)
            response = f"AI Response to your message: {gen_ai_response}"
            return Response({"message": response}, status=status.HTTP_200_OK)
