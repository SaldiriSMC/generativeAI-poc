from django.contrib.auth import views as auth_views
from django.urls import path

import rag_ai.views
from accounts import views
from accounts.views import LoginViewAPI, RegisterAPIView, UpdateUserProfileAPI, PasswordUpdateAPIView, UserAIChatView

urlpatterns = [
    # Account management URLs
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Optional logout.html URL
    path('user-logout/', views.user_logout, name='user-logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('profile/', rag_ai.views.gen_ai_chat, name='gen_ai_chat'),
    path('user-account-update/', views.user_update, name='user_account_update'),
    path('update-password/', views.update_password, name='update_password'),
    path('ai-docs-upload/', views.gen_ai_chat_docs_upload, name='ai_doc_upload'),
    path('model-creds-add/', views.groq_pinecone_apis_add, name='model_creds_add'),
    path('model-creds-update/<int:pk>/', views.groq_pinecone_apis_update, name='model_creds_update'),
    path('model-update-env/<int:pk>/', views.update_key_on_env_variable, name='model_update_env'),
    path('api-model-list/', views.ai_api_keys_model_list, name='api_model_list'),
    path('api-model-list-update/', views.ai_api_keys_model_list_update, name='api_model_list_update'),

    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('api-login/', LoginViewAPI.as_view(), name='api_login'),
    path('register-api/', RegisterAPIView.as_view(), name='register_api'),
    path('update-profile/', UpdateUserProfileAPI.as_view(), name='update_profile'),
    path('api/password/update/', PasswordUpdateAPIView.as_view(), name='password-update-api'),
    path('api/ai-chat/', UserAIChatView.as_view(), name='api-ai-chat'),
]
