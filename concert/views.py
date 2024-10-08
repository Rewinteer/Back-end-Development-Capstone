from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, reverse
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req


# Create your views here.

def signup(request):
    if request.method == "GET":
        return render(request, "signup.html", {"form": SignUpForm})
    elif request.method == "POST":        
        try:
            username = request.POST["username"]
            password = request.POST["password"]
            user = User.objects.filter(username=username)
            if not user:
                user = User(username=username, password=make_password(password))
                user.save()
                return redirect(reverse('index'))
            else:
                return render(request, "signup.html", {"form": SignUpForm, "message": "user already exist"})
        except KeyError:
            return render(request, "signup.html", {"form": SignUpForm})


def index(request):
    return render(request, "index.html")


def songs(request):
    songs = {"songs":[{"id":1,"title":"duis faucibus accumsan odio curabitur convallis","lyrics":"Morbi non lectus. Aliquam sit amet diam in magna bibendum imperdiet. Nullam orci pede, venenatis non, sodales sed, tincidunt eu, felis."}]}
    return render(request, "songs.html", {"songs": songs["songs"]})


def photos(request):
    photos = [{
    "id": 1,
    "pic_url": "http://dummyimage.com/136x100.png/5fa2dd/ffffff",
    "event_country": "United States",
    "event_state": "District of Columbia",
    "event_city": "Washington",
    "event_date": "11/16/2022"}]
    return render(request, "photos.html", {"photos": photos})
    

def login_view(request):
    if request.method == "POST":
        try:
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect(reverse("index"))
            else:
                return render(request, "login.html", {"form": LoginForm, "message": "wrong credentials"})
        except KeyError:
            return render(request, "login.html", {"form": LoginForm, "message": "username and/or password is empty"})
    return render(request, "login.html", {"form": LoginForm})

def logout_view(request):
    logout(request)
    return redirect(reverse("login"))

def concerts(request):
    if request.user.is_authenticated:
        list_of_concerts = []
        concert_objects = Concert.objects.all()
        for concert in concert_objects:
            try:
                status = concert.attendee.filter(user=request.user).first().attending
            except:
                status = "-"
            list_of_concerts.append(
                {
                    "concert": concert,
                    "status": status
                }
            )
        return render(request, "concerts.html", {"concerts": list_of_concerts})
    else:
        return redirect(reverse("login"), {"form": LoginForm})


def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = Concert.objects.get(pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
