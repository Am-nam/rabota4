from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import News, Comment


# -----------------------
# ГЛАВНАЯ СТРАНИЦА
# -----------------------
def home(request):
    latest_news = News.objects.order_by('-created_at')[:3]
    return render(request, 'home.html', {'latest_news': latest_news})


# -----------------------
# СПИСОК НОВОСТЕЙ
# (поиск + сортировка + дата)
# -----------------------
def news_list(request):
    query = request.GET.get('q')
    sort = request.GET.get('sort')
    date = request.GET.get('date')

    news = News.objects.all()

    # поиск
    if query:
        news = news.filter(title__icontains=query)

    # фильтр по дате
    if date:
        news = news.filter(created_at__date=date)

    # сортировка
    if sort == 'old':
        news = news.order_by('created_at')
    else:
        news = news.order_by('-created_at')

    return render(request, 'news_list.html', {
        'news': news
    })


# -----------------------
# СТРАНИЦА НОВОСТИ + КОММЕНТАРИИ
# -----------------------
def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    comments = news_item.comments.all().order_by('-created_at')

    if request.method == "POST":
        if request.user.is_authenticated:
            text = request.POST.get('text')
            if text:
                Comment.objects.create(
                    news=news_item,
                    user=request.user,
                    text=text
                )
            return redirect('news_detail', pk=pk)

    return render(request, 'news_detail.html', {
        'news': news_item,
        'comments': comments
    })


# -----------------------
# КОНТАКТЫ
# -----------------------
def contacts(request):
    return render(request, 'contacts.html')


# -----------------------
# ВХОД
# -----------------------
def user_login(request):
    error = None

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            error = "Неверный логин или пароль"

    return render(request, 'login.html', {'error': error})


# -----------------------
# ВЫХОД
# -----------------------
def user_logout(request):
    logout(request)
    return redirect('home')


# -----------------------
# РЕГИСТРАЦИЯ
# -----------------------
def register(request):
    error = None

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            error = "Пользователь уже существует"
        else:
            User.objects.create_user(username=username, password=password)
            return redirect('login')

    return render(request, 'register.html', {'error': error})