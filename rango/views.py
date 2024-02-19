from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def index(request):
    # # return HttpResponse("Rango says hey there partner! <a href='/rango/about/'>About</a>")
    # # Construct a dictionary to pass to the template as its context.
    # context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}

    # # Return a rendered response to send to the client.
    # # We make use of the shortcut function, the first paramter is the template we wish to use
    # return render(request, 'rango/index.html', context=context_dict)

    # Query the database for a list of ALL categories currently stored
    
    # Order the categories by the number of likes in descending order
    
    # Retrieve the top 5 only -- or all if less than 5
    
    # Place the list in our context_dic dictionary (along with the boldmessage) that will be 
    # passed to the template engine

    category_list = Category.objects.order_by('-likes')[:5]

    # Retrieve the top five most viewed pages
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # Return the response
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    # return HttpResponse("Rango says here is the about page. <a href='/rango/'>Index</a>")

    context_dict = {'boldmessage': "This tutorial has been put together by " , 'emphasismessage': "Saranya Arul"}

    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    # create a context dictionary which we can pass to the
    # template rendering engine
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we cannot find, the .get() method raises an DoesNotExit exception
        # Thus, .get() returns one model instance or raises an exception
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the assosicated pages
        # The filter() will return the list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages
        context_dict['pages'] = pages

        # We also add the category object from the database to the context dictionary
        # We'll use this in the template to check if the category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We enter here if we did not find the specified category
        # Do not do anything - the template will just display 
        # "no category" found message
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    # Functionalities
    # Showing a new, blank form for adding a category
    # Saving form data provided by the user to the associated model, and redirecting to the Rango homepage
    # If there are errors, redisplay the form with error messages
    form = CategoryForm()

    # A HTTP POST
    if request.method == 'POST':
        form = CategoryForm(request.POST);

        # Is the form a valid one?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            # Now that the category is saved, we could confirm this.
            # For now, just redirect the user back to the index view.
            return redirect('/rango/')
        else:
            # The supplied form has errors
            # Printing the error in the console
            print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages(if any).
    return render(request, 'rango/add_category.html', {'form':form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # You cannot add a page to a Category that does not exist
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
            else:
                print(form.errors)
        
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    # A boolean value for telling the template whether
    # the registration was successful. Set to false by
    # default. Code changes the value to True after
    # successful registration
    registered = False

    # If it is a HTTP POST, we are interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both the UserForm and UserProfileForm

        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        # If the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we cna update the user object.
            user.set_password(user.password)
            user.save();


            # Now sort out the UserProfile instance
            # Since we need to set the user attribute ourselves
            # we set commit=False. This delays saving the model util 
            # we are ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture
            # If so, we need to get it from the input form and put
            # it in the UserProfile model

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # now we save the Userprofile model instance
            profile.save()

            # Update out variable to indicate that the template
            # registration was successful
            registered = True
        else:
            # Invalid form or forms - mistakes or something went wrong
            # Print the problems to the terminal
            print(user_form.errors, profile_form.errors)

    else:
        # Not a HTTP POST, so we render our form using the two
        # ModelForm instances. These forms will be blank, ready
        # for user input
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context
    return render(request, 
                    'rango/register.html', 
                    context = {'user_from': user_form,
                                'profile_form': profile_form,
                                 'registered': registered})

def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information
    if request.method == 'POST':
        # Gather the username and password provided by the user in the login form
        # We use request.POST.get('<variable>') as opposed to 
        # request.POST['<variable'>], because the former returns None if the value
        # does not exist, while the later will raise a KeyError exception

        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is valid
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (absence of a value), no user with matching 
        # credentials was found

        if user:
            # Is the account active? It could have been disabled
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We will send the user back to the homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we cannot log the user in
            print(f"Invalid login details:{username}, {password}")
            return HttpResponse("Invalid login details given")
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET
    else:
        # No context varaibles to pass to the template system, hence the blank
        # dictionary object...
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

# Use the login_required() ecaorator to ensure only those logged in can
# access the view

@login_required
def user_logout(request):
    # Since we know that the user is logged in, we can now just log them out
    logout(request)
    # Take the user back to the homepage
    return redirect(reverse('rango:index'))



        