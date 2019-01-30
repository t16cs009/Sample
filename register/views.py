from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
    )
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render, resolve_url
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, EmailTextForm
)
from scalendar.views import (
    MonthCalendarMixin, WeekCalendarMixin,
    WeekWithScheduleMixin, MonthWithScheduleMixin
)
import datetime
import calendar
from django.shortcuts import redirect
from django.views import generic
from scalendar.forms import BS4ScheduleForm, SimpleScheduleForm
from scalendar.forms import BS4ScheduleForm
from django.contrib.auth.models import User
from django.shortcuts import render

from django.core.mail import EmailMessage
from django.http import HttpResponse
from register import mixins
from scalendar.models import Schedule, Decision
# Create your views here.


User = get_user_model()

class Top(generic.TemplateView):
    template_name = 'register/top.html' # register の top.html を参照


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm # register の forms.py の LoginForm を設ける
    template_name = 'register/login.html'


class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'register/top.html'


class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'register/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject_template = get_template('register/mail_template/create/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('register/mail_template/create/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        return redirect('register:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'register/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'register/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoenNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # まだ仮登録で、他に問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()

class OnlyYouMixin(UserPassesTestMixin):
    """本人か、スーパーユーザーだけユーザーページアクセスを許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser

class OnlySuperuser(UserPassesTestMixin):
    """UserPassesTestMixin ログインし、特定のユーザにのみ表示を行なう"""
    """スーパーユーザーだけに閲覧を許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.is_superuser

class Management(OnlySuperuser, generic.TemplateView):
    '''管理者の専用ページ'''
    model = User
    template_name = 'register/management.html'

class DecisionNumbers(OnlySuperuser, generic.TemplateView):
    '''シフトの人数の調整ページ'''
    model = User
    template_name = 'register/decision_numbers.html'

class MonthWithFormsCalendar(mixins.MonthWithFormsMixin, generic.View):
    """フォーム付きの月間カレンダーを表示するビュー"""
    template_name='register/month_with_forms.html'
    model = Decision
    date_field = 'date'
    form_class = SimpleScheduleForm

    def get(self, request, **kwargs):
        context = self.get_month_calendar()
        # last_date = calendar.monthrange(context['month']['current'].year, context['month']['current'].month)[1]

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        context = self.get_month_calendar()
        formset = context['month_formset']
        if formset.is_valid():
            formset.save()
            return redirect('register:month_with_forms')

        return render(request, self.template_name, context)


class Mail(OnlySuperuser, MonthCalendarMixin, WeekWithScheduleMixin, generic.CreateView):
    '''メール送信ページ'''
    model = User
    template_name = 'register/mail.html'

    form_class = EmailTextForm

    def get_context_data(self, **kwargs):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        day = self.kwargs.get('day')
        if month and year and day:
            date = datetime.date(year=int(year), month=int(month), day=int(day))
        else:
            date = datetime.date.today()

        context = super().get_context_data(**kwargs)
        context['week'] = self.get_week_calendar()
        context['month'] = self.get_month_calendar()
        context['selected_date'] = date
        return context

    def form_valid(self, form):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        day = self.kwargs.get('day')
        if month and year and day:
            date = datetime.date(year=int(year), month=int(month), day=int(day))
        else:
            date = datetime.date.today()
        schedule = form.save(commit=False)
        schedule.date = date
        for staff in User.objects.all():
            EmailMessage(str(schedule.date) + 'kiknkyuu', schedule.description +'', to = [staff.email]).send()
        return redirect('register:mail', year=date.year, month=date.month, day=date.day)

class Config(generic.TemplateView):
    '''設定を行なうページ'''
    model = User
    template_name = 'register/config.html'

class StaffIndex(generic.TemplateView):
    '''スタッフの表示を行なうページ'''
    model = User
    template_name = 'register/staff_index.html'

    def get_context_data(self, **kwargs):
        context =  generic.TemplateView.get_context_data(self, **kwargs)
        context['users'] = User.objects.all()
        return context

class StaffDelete(OnlySuperuser, generic.DeleteView):
    '''メール送信ページ'''
    model = User
    form_class = UserUpdateForm
    template_name = 'register/staff_delete.html'
    success_url = reverse_lazy('register:staff_index')


class UserDetail(OnlyYouMixin, generic.DetailView):
    """ユーザーの詳細ページ"""
    model = User
    template_name = 'register/user_detail.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    """ユーザー情報更新ページ"""
    model = User
    form_class = UserUpdateForm
    template_name = 'register/user_form.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く

    def get_success_url(self):
        return resolve_url('register:user_detail', pk=self.kwargs['pk'])


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('register:password_change_done')
    template_name = 'register/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'register/password_change_done.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'register/mail_template/password_reset/subject.txt'
    email_template_name = 'register/mail_template/password_reset/message.txt'
    template_name = 'register/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('register:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'register/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('register:password_reset_complete')
    template_name = 'register/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'register/password_reset_complete.html'




class MyCalendar(MonthCalendarMixin, WeekWithScheduleMixin, generic.CreateView):
    """月間カレンダー、週間カレンダー、スケジュール登録画面のある欲張りビュー"""
    template_name = 'register/mycalendar.html'
    form_class = BS4ScheduleForm

    def get_context_data(self, **kwargs):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        day = self.kwargs.get('day')
        if month and year and day:
            date = datetime.date(year=int(year), month=int(month), day=int(day))
        else:
            date = datetime.date.today()

        context = super().get_context_data(**kwargs)
        context['week'] = self.get_week_calendar()
        context['month'] = self.get_month_calendar()
        context['selected_date'] = date
        return context

    def form_valid(self, form):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        day = self.kwargs.get('day')
        if month and year and day:
            date = datetime.date(year=int(year), month=int(month), day=int(day))
        else:
            date = datetime.date.today()
        schedule = form.save(commit=False)
        schedule.user_name = self.request.user
        schedule.date = date
        schedule.save()
        return redirect('register:mycalendar', year=date.year, month=date.month, day=date.day)

class MonthWithScheduleCalendar(MonthWithScheduleMixin, mixins.MonthWithScheduleMixin, generic.TemplateView):
    """スケジュール付きの月間カレンダーを表示するビュー"""
    template_name = 'register/month_with_schedule.html'
    model = Decision
    data_field = 'date'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = super().get_context_data(**kwargs)
        context['month'] = self.get_month_calendar()
        return context


def index(request):
   EmailMessage(u'件名', u'本文', to = ['sakamichi.214@gmail.com']).send()
   return HttpResponse('Send your register email')

