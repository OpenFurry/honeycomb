from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    BanForm,
)
from .models import (
    Ban,
    Flag,
)
# from activitystream.models import Activity
# from usermgmt.models import Notification


@permission_required('administration.can_list_bans', raise_exception=True)
@staff_member_required
def list_bans(request):
    if request.GET.get('all'):
        bans = Ban.objects.all()
    else:
        bans = Ban.objects.filter(active=True)
    return render(request, 'list_bans.html', {
        'bans': bans,
        'tab': 'bans',
        'showing_inactive': request.GET.get('all'),
    })


@permission_required('administration.can_list_bans', raise_exception=True)
@login_required
def list_participating_bans(request):
    query = Q(admin_contact=request.user)
    if request.GET.get('all') is None:
        query &= Q(active=True)
    bans = Ban.objects.filter(query)
    return render(request, 'list_bans.html', {
        'bans': bans,
        'tab': 'bans',
        'showing_inactive': request.GET.get('all')
    })


@permission_required('administration.can_ban_users', raise_exception=True)
@staff_member_required
def create_ban(request):
    if request.method == 'GET':
        user = get_object_or_404(User, username=request.GET.get('user'))
    else:
        user = get_object_or_404(User, pk=request.POST.get('user'))
    if user == request.user or user.is_superuser:
        messages.error(request, "You cannot ban yourself or superusers.")
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)

    if not user.is_active:
        messages.error(request, "You cannot ban an inactive user.")
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)

    form = BanForm(initial={
        'user': user,
        'end_date': timezone.now(),
        'flags': Flag.objects.filter(pk=request.GET.get('flag')),
    })
    form.fields['flags'].queryset = Flag.objects.filter(
        flagged_object_owner=user)
    if request.method == 'POST':
        form = BanForm(request.POST)
        if form.is_valid():
            ban = form.save(commit=False)
            ban.admin_contact = request.user
            ban.save()
            form.save_m2m()
            ban.user.profile.banned = True
            ban.user.profile.save()
            return redirect(ban.get_absolute_url())
    return render(request, 'create_ban.html', {
        'form': form,
        'tab': 'bans',
    })


@permission_required('administration.can_view_bans', raise_exception=True)
@staff_member_required
def view_ban(request, ban_id=None):
    ban = get_object_or_404(Ban, pk=ban_id)
    return render(request, 'view_ban.html', {
        'title': "{}'s ban".format(ban.user.profile.get_display_name()),
        'ban': ban,
        'tab': 'bans',
    })


@permission_required('administration.can_lift_bans', raise_exception=True)
@staff_member_required
@require_POST
def lift_ban(request, ban_id=None):
    ban = get_object_or_404(Ban, pk=ban_id)
    ban.active = False
    ban.save()
    ban.user.profile.banned = False
    ban.user.profile.save()
    ban.user.is_active = True
    ban.user.save()
    messages.success(request, "Ban lifted.")
    return redirect(ban.get_absolute_url())


def ban_notice(request, ban_id=None, ban_hash=None):
    ban = get_object_or_404(Ban, pk=ban_id, user_has_viewed=False)
    if ban_hash != ban.get_ban_hash() or request.user != ban.user:
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    ban.user.is_active = False
    ban.user.save()
    logout(request)
    return render(request, 'view_ban.html', {
        'title': 'Your account has been disabled',
        'ban': ban,
        'tab': 'bans',
    })
