from django.urls import path
from . import views
from scalendar import views as s_views 
app_name = 'register'

urlpatterns = [
    
    path('', views.Top.as_view(), name='top'), # register の view.py の class Top を参照
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done/', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('user_detail/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('user_update/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('mycalendar/', views.MyCalendar.as_view(), name='mycalendar'),
    path('mycalendar/delete/<int:id>', s_views.delete, name='delete'),
    path('mycalendar/<int:year>/<int:month>/<int:day>/', views.MyCalendar.as_view(), name='mycalendar'),
    path('month_with_schedule/',views.MonthWithScheduleCalendar.as_view(), name='month_with_schedule'),
    path('month_with_schedule/',views.MonthWithScheduleCalendar.as_view(), name='month_with_schedule'),
    path('month_with_schedule/<int:year>/<int:month>/',views.MonthWithScheduleCalendar.as_view(), name='month_with_schedule'),

    path('sendmail/', views.index, name='sendmail'),

    path('management/', views.Management.as_view(), name='management'),
    path('management/decision_numbers/', views.DecisionNumbers.as_view(), name='decision_numbers'),
    path('management/mail/', views.Mail.as_view(), name='mail'),
    path('config/', views.Config.as_view(), name='config'),

    
]
