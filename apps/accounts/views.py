from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import User, Classroom
from .forms import RegisterForm, ProfileForm, ClassroomForm


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    features = [
        ('fas fa-mouse-pointer', 'Sürükle & Bırak', 'Öğrenciler nesneleri doğru kutucuklara sürükler.'),
        ('fas fa-list-ul', 'Çoktan Seçmeli', 'Klasik çoktan seçmeli sorular oluşturun.'),
        ('fas fa-link', 'Eşleştirme', 'İki sütun arasında öğeleri birbirine bağlayın.'),
        ('fas fa-microphone', 'Sesli Yanıt', 'Öğrenciler mikrofon ile sözlü cevap verebilir.'),
        ('fab fa-youtube', 'Video Entegrasyonu', 'YouTube/Vimeo videolarını kağıda gömin.'),
        ('fas fa-bolt', 'Anında Puanlama', 'Sistem cevapları otomatik değerlendirir ve puan verir.'),
    ]
    return render(request, 'home.html', {'features': features})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Hesabınız başarıyla oluşturuldu!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'E-posta veya şifre hatalı.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    user = request.user
    context = {}
    if user.is_teacher:
        from apps.worksheets.models import Worksheet
        from apps.assignments.models import Assignment
        context['my_worksheets'] = Worksheet.objects.filter(author=user).order_by('-created_at')[:6]
        context['my_classrooms'] = Classroom.objects.filter(teacher=user)
        context['my_assignments'] = Assignment.objects.filter(created_by=user).order_by('-created_at')[:5]
        context['total_students'] = User.objects.filter(
            enrolled_classrooms__teacher=user
        ).distinct().count()
    else:
        from apps.assignments.models import Assignment
        from apps.submissions.models import Submission
        context['my_assignments'] = Assignment.objects.filter(
            classrooms__students=user
        ).distinct().order_by('-due_date')[:5]
        context['my_submissions'] = Submission.objects.filter(
            student=user
        ).order_by('-submitted_at')[:5]
        context['enrolled_classrooms'] = user.enrolled_classrooms.all()
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil güncellendi.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def classroom_list(request):
    if request.user.is_teacher:
        classrooms = Classroom.objects.filter(teacher=request.user)
    else:
        classrooms = request.user.enrolled_classrooms.all()
    return render(request, 'accounts/classroom_list.html', {'classrooms': classrooms})


@login_required
def classroom_create(request):
    if not request.user.is_teacher:
        messages.error(request, 'Bu sayfaya sadece öğretmenler erişebilir.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.teacher = request.user
            classroom.save()
            messages.success(request, f'"{classroom.name}" sınıfı oluşturuldu. Kod: {classroom.code}')
            return redirect('classroom_detail', pk=classroom.pk)
    else:
        form = ClassroomForm()
    return render(request, 'accounts/classroom_form.html', {'form': form})


@login_required
def classroom_detail(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if classroom.teacher != request.user and request.user not in classroom.students.all():
        messages.error(request, 'Bu sınıfa erişim izniniz yok.')
        return redirect('dashboard')
    return render(request, 'accounts/classroom_detail.html', {'classroom': classroom})


@login_required
def join_classroom(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        classroom = Classroom.objects.filter(code=code).first()
        if classroom:
            classroom.students.add(request.user)
            messages.success(request, f'"{classroom.name}" sınıfına katıldınız!')
        else:
            messages.error(request, 'Geçersiz sınıf kodu.')
    return redirect('dashboard')
