import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django
django.setup()

from rango.models import Category, Page
from random import randint

def populate():
    views = 128
    likes = 64
    python_cat = add_cat('Python', views, likes)

    add_page(cat=python_cat,
        title="Official Python Tutorial",
        url="http://docs.python.org/2/tutorial/",
        views=randint(0,100))

    add_page(cat=python_cat,
        title="How to Think like a Computer Scientist",
        url="http://www.greenteapress.com/thinkpython/",
        views=randint(0,100))

    add_page(cat=python_cat,
        title="Learn Python in 10 Minutes",
        url="http://www.korokithakis.net/tutorials/python/",
        views=randint(0,100))

    views /=2
    likes /=2
    django_cat = add_cat("Django", views, likes)

    add_page(cat=django_cat,
        title="Official Django Tutorial",
        url="https://docs.djangoproject.com/en/1.5/intro/tutorial01/",
        views=randint(0,100))

    add_page(cat=django_cat,
        title="Django Rocks",
        url="http://www.djangorocks.com/",
        views=randint(0,100))

    add_page(cat=django_cat,
        title="How to Tango with Django",
        url="http://www.tangowithdjango.com/",
        views=randint(0,100))

    views /=2
    likes /=2
    frame_cat = add_cat("Other Frameworks", views, likes)

    add_page(cat=frame_cat,
        title="Bottle",
        url="http://bottlepy.org/docs/dev/",
        views=randint(0,100))

    add_page(cat=frame_cat,
        title="Flask",
        url="http://flask.pocoo.org",
        views=randint(0,100))

    personal_cat = add_cat("Mihail Yanev")
    add_page(cat=personal_cat,
             title="git repo for this project",
             url="https://github.com/2065983Y/tangowithdjango")

    add_page(cat=personal_cat,
             title="link to personal pythonanywhere",
             url="https://www.pythonanywhere.com/user/2065983Y/account/")
    

    # Print out what we have added to the user.
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print "- {0} - {1}".format(str(c), str(p))

def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title, url=url, views=views)[0]
    return p

def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name, views = views, likes = likes)[0]
    return c

# Start execution here!
if __name__ == '__main__':
    print "Starting Rango population script..."
    populate()
