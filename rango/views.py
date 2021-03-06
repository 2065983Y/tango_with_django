from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from rango.models import Category, UserProfile
from rango.models import Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm, UserEditForm
from rango.bing_search import run_query

def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return redirect('/rango/category/' + category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category_name_url': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)



# Create your views here.
def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response



def about(request):
    context_dict = {"secret": 'Rango dem joker hue hue'}
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    context_dict['visits'] = count
    return render(request, 'rango/about.html', context_dict)


# return HttpResponse("""Rango says here's dem about page lul
#	<br/> <a href="/rango"> Home </a>
#	""")

def category(request, category_name_slug):
    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        print "Query: ", query
        if query:
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query
    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        context_dict['category_name_url'] = category_name_slug
        print "\n\n\n", context_dict['category_name_url']

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        return redirect('/rango/')

    if not context_dict['query']:
        context_dict['query'] = category.name

        # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)


    return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):
    print request
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

def register_profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user

            if 'picture' in request.FILES:
                profile.avatar = request.FILES['picture']
            profile.save()
            return redirect("/rango")
        else:
            print profile_form.errors
    else:
        profile_form = UserProfileForm()


    return render(request, 'rango/profile_registration.html', {'profile_form': profile_form})

@login_required
def profile_no_edit(request):
    context_dict = {}
    user = User.objects.get(username=request.user)


    try:
        user_profile = UserProfile.objects.get(user=user)
    except:
        user_profile = None

    context_dict['user'] = user
    context_dict['user_profile'] = user_profile
    return render(request, 'rango/profile.html', context_dict)

    #if request.method == 'POST':
    #    user_profile = UserProfileForm(data=request.POST)


@login_required
def profile(request):
    context_dict = {}
    print "METHOD", request.method
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST, instance=request.user)
        profile_form = UserProfileForm(data=request.POST, instance=request.user.userprofile)

        if profile_form.is_valid and user_form.is_valid:
            profile = profile_form.save(commit=False)
            user = user_form.save(commit=False)
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            user.save()
            profile.save()
        else:
            print user_form.errors
            print profile_form.errors
    else:
        user_form = UserEditForm(instance=request.user)
        try:
            profile_form = UserProfileForm(instance=request.user.userprofile)
        except:
            profile_form = None
    context_dict['user_form'] = user_form
    if profile_form:
        context_dict['profile_form'] = profile_form
        context_dict['picture'] = request.user.userprofile.picture
    return render(request, "rango/profile.html", context_dict)

@login_required
def users(request):
    users=User.objects.order_by('username')
    return render(request,'rango/users.html',{'users':users})



def get_category_list(max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
                cat_list = Category.objects.filter(name__istartswith=starts_with)
       # else:
       #     cat_list = Category.objects.all()

        if max_results > 0:
                if len(cat_list) > max_results:
                        cat_list = cat_list[:max_results]

        return cat_list

def suggest_category(request):

        cat_list = []
        starts_with = ''
        if request.method == 'GET':
                starts_with = request.GET['suggestion']

        cat_list = get_category_list(8, starts_with)

        return render(request, 'rango/category_list.html',
                      {'cat_list': cat_list })
