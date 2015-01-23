from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
	return HttpResponse(
		"<HTML> Rango says wut up daug? <br/>\
		<a href='/rango/about'>About</a></HTML>")

def about(requtest):
	return HttpResponse("""Rango says here's dem about page lul 
		<br/> <a href="/rango"> Home </a>
		""")

