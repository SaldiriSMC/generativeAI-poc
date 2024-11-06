import magic
import six
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import render, redirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.forms import UserRegisterForm, UserLoginForm, UserUpdateForm, PasswordUpdateForm, AIDocsUploaderForm, \
    UserAICredsForm
from accounts.models import UserAICreds
from accounts.serializers import LoginSerializer, UserSerializer, UserRegisterSerializer, UserUpdateSerializer, \
    PasswordUpdateSerializer, UserQuerySerializer
from vect_db import user_chat_ai, vec_db_data_transfer, api_keys_gorq_pinecone


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


@login_required
def user_logout(request):
    return render(request, 'registration/logout.html')


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
                decoded_text = file_content.decode('utf-8')
                api_keys = request.user.ai_creds.filter(is_active=True).first()
                if api_keys:
                    pc, database_name, pinecone_index, client = api_keys_gorq_pinecone(
                        api_keys.pinecone_api_key,
                        api_keys.pinecone_index_name,
                        api_keys.groq_api_key)
                else:
                    pc, database_name, pinecone_index, client = api_keys_gorq_pinecone()
                data_send_to_db = vec_db_data_transfer(file_name, decoded_text, pc, database_name, pinecone_index)
                if data_send_to_db:
                    messages.success(request, 'Your document has been successfully uploaded.')
                    return redirect('ai_doc_upload')
                messages.error(request, 'There was an issue uploading your document.')
                return redirect('ai_doc_upload')
            else:
                messages.error(request, 'Your file must be a .txt file, under 12 KB, and plain text.')
                return redirect('ai_doc_upload')

        messages.error(request, 'Please correct the errors below.')
        return redirect('ai_doc_upload')

    form = AIDocsUploaderForm()
    return render(request, 'registration/ai_file_upload.html', {'form': form})


@login_required
def groq_pinecone_apis_add(request):
    if request.method == 'POST':
        form = UserAICredsForm(request.POST)
        if form.is_valid():
            add_ai_keys = UserAICreds(
                user=request.user,
                name_keys_object=form.cleaned_data['name_keys_object'],
                pinecone_api_key=form.cleaned_data['pinecone_api_key'],
                pinecone_index_name=form.cleaned_data['pinecone_index_name'],
                groq_api_key=form.cleaned_data['groq_api_key'],
            )
            add_ai_keys.save()
            messages.success(request, 'Your AI key has been added.')
            return redirect('model_creds_add')
        messages.success(request, 'Kindly resolve the errors below.')
        return redirect('model_creds_add')
    form = UserAICredsForm()
    return render(request, 'registration/user_ai_model_add.html', {'form': form})


@login_required
def ai_api_keys_model_list(request):
    user_api_models = UserAICreds.objects.filter(user=request.user)
    return render(request, 'registration/ai_api_keys_model_list.html',
                  {'user_api_models': user_api_models})


@login_required
def ai_api_keys_model_list_update(request):
    user_api_models_update = UserAICreds.objects.filter(user=request.user)
    return render(request, 'registration/ai_api_keys_model_list_update.html',
                  {'user_api_models_update': user_api_models_update})


@login_required
def groq_pinecone_apis_update(request, pk):
    api_model_update_object = UserAICreds.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = UserAICredsForm(request.POST)
        if form.is_valid():
            api_model_update_object.user = request.user
            api_model_update_object.name_keys_object = form.cleaned_data['name_keys_object']
            api_model_update_object.pinecone_api_key = form.cleaned_data['pinecone_api_key']
            api_model_update_object.pinecone_index_name = form.cleaned_data['pinecone_index_name']
            api_model_update_object.groq_api_key = form.cleaned_data['groq_api_key']
            api_model_update_object.save()
            messages.success(request, 'Your AI key has been updated.')
            return redirect('model_creds_update', pk=api_model_update_object.pk)
        messages.error(request, 'Please correct the errors below.')
        return redirect('model_creds_update', pk=api_model_update_object.pk)
    form = UserAICredsForm(instance=api_model_update_object)
    return render(request, 'registration/user_ai_model_update.html',
                  {'form': form, 'object': api_model_update_object.id})


@login_required
def update_key_on_env_variable(request, pk):
    UserAICreds.objects.filter(user=request.user).update(is_active=False)
    UserAICreds.objects.filter(pk=pk).update(is_active=True)
    messages.success(request, 'Model API Keys Updated')
    return redirect('gen_ai_chat')


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
            if request.user.ai_creds:
                api_keys = request.user.ai_creds.filter(is_active=True).first()
                pc, database_name, pinecone_index, client = api_keys_gorq_pinecone(
                    api_keys.pinecone_api_key,
                    api_keys.pinecone_index_name,
                    api_keys.groq_api_key)
            else:
                pc, database_name, pinecone_index, client = api_keys_gorq_pinecone()
            gen_ai_response = user_chat_ai(message, pc, pinecone_index, client)
            response = f"AI Response to your message: {gen_ai_response}"
            return Response({"message": response}, status=status.HTTP_200_OK)
