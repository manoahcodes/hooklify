from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def profile_list_view(request, *args, **kwargs):
    context = {
        "object_list": User.objects.filter(is_active=True)
    }
    return render(request, "profiles/list.html", context)

@login_required
def profile_view(request, *args, username=None, **kwargs):
    user = request.user
    profile_user = get_object_or_404(User, username=username)
    is_me =  profile_user == user
    if is_me:
        if user.has_perm("visits.view_pagevisit"):
            pass
            # qs = PageVisit.objects.all()
    return HttpResponse(f"Profile view: {username} - {profile_user.id}")

@login_required
def profile_detail_view(request, *args, username=None, **kwargs):
    user = request.user
    user_groups = user.groups.all()
    print("User groups:", user_groups)
    profile_user = get_object_or_404(User, username=username)
    is_me =  profile_user == user
    context = {
        "object": profile_user,
        "instance": profile_user,
        "is_me": is_me,
    }
    return render(request, "profiles/details.html", context)