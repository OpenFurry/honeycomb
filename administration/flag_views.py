from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    FlagForm,
)
from .models import (
    Flag,
)
from usermgmt.models import Notification


@permission_required('administration.can_list_social_flags',
                     raise_exception=True)
@permission_required('administration.can_list_content_flags',
                     raise_exception=True)
@staff_member_required
def list_all_flags(request):
    if request.GET.get('all'):
        flags = Flag.objects.all()
    else:
        flags = Flag.objects.filter(resolved=None)
    return render(request, 'list_flags.html', {
        'title': 'All flags',
        'flags': flags,
        'tab': 'flags',
    })


@permission_required('administration.can_list_social_flags',
                     raise_exception=True)
@staff_member_required
def list_social_flags(request):
    flags = Flag.objects.filter(flag_type=Flag.SOCIAL)
    return render(request, 'list_flags.html', {
        'title': 'Social flags',
        'flags': flags,
        'tab': 'flags',
    })


@permission_required('administration.can_list_content_applications',
                     raise_exception=True)
@staff_member_required
def list_content_flags(request):
    flags = Flag.objects.filter(flag_type=Flag.CONTENT)
    return render(request, 'list_flags.html', {
        'title': 'Social flags',
        'flags': flags,
        'tab': 'flags',
    })


@login_required
def create_flag(request):
    # Ensure that we have both content type and object id
    if 'content_type' not in request.GET or 'object_id' not in request.GET:
        return render(request, 'permission_denied.html', {
            'title': 'Cannot create flag without a subject',
            'additional_error': 'Flags must be related to an object',
        }, status=403)

    # Ensure that we can flag the given content type
    if request.GET.get('content_type') not in \
            settings.FLAGGABLE_CONTENT_TYPES:
        return render(request, 'permission_denied.html', {
            'title': 'That content type is not flaggable',
            'additional_error':
                'The flaggable content types are <ul>{}</ul>'.format(
                    ''.join([
                        '<li>'+c+'</li>' for c in
                        settings.FLAGGABLE_CONTENT_TYPES
                    ])
                ),
        }, status=403)

    # Retrieve the content type and object
    parts = request.GET.get('content_type').split(':')
    ctype = get_object_or_404(ContentType, app_label=parts[0], model=parts[1])
    obj = ctype.get_object_for_this_type(pk=request.GET.get('object_id'))

    # Ensure that we can flag the given object
    if hasattr(obj, 'owner') and obj.owner == request.user:
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
            'additional_error': 'You cannot flag your own objects',
        }, status=403)
    form = FlagForm(instance=Flag(
        content_type=ctype,
        object_id=obj.id,
    ))

    # Try to save any POSTed data
    if request.method == 'POST':
        form = FlagForm(request.POST)
        if form.is_valid():
            flag = form.save(commit=False)
            flag.flagged_by = request.user
            flag.flagged_object_owner = (request.user if not
                                         hasattr(flag.object_model, 'owner')
                                         else flag.object_model.owner)
            flag.save()
            form.save_m2m()
            flag.participants.add(request.user)
            flag.participants.add(flag.flagged_object_owner)
            return redirect(flag.get_absolute_url())
    return render(request, 'create_flag.html', {
        'title': 'Flag {}'.format(ctype.model),
        'subtitle': str(obj),
        'form': form,
    })


@login_required
def view_flag(request, flag_id=None):
    flag = get_object_or_404(Flag, pk=flag_id)
    social = 'administration.can_view_social_applications'
    content = 'administration.can_view_content_applications'
    if request.user not in flag.participants.all() and not \
            (not (request.user.has_perm(social) and
                  flag.flag_type == Flag.SOCIAL) or
             not (request.user.has_perm(content) and
                  flag.flag_type == Flag.CONTENT)):
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    title = "{}'s flag".format(
        flag.flagged_by.profile.get_display_name())
    return render(request, 'view_flag.html', {
        'title': title,
        'flag': flag,
        'tab': 'flags',
    })


@login_required
def list_participating_flags(request):
    query = Q(participants__in=[request.user])
    if request.GET.get('all') is None:
        query &= Q(resolved=None)
    flags = Flag.objects.filter(query)
    return render(request, 'list_flags.html', {
        'title': 'My flags',
        'flags': flags,
        'tab': 'flags',
    })


@staff_member_required
@require_POST
def join_flag(request, flag_id=None):
    flag = get_object_or_404(Flag, pk=flag_id)
    social = 'administration.can_view_social_applications'
    content = 'administration.can_view_content_applications'
    if not ((request.user.has_perm(social) and
             flag.flag_type == Flag.SOCIAL) or
            (request.user.has_perm(content) and
             flag.flag_type == Flag.CONTENT)):
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    if request.user in flag.participants.all():
        messages.warning(request,
                         'You are already a participant in this flag')
    else:
        for participant in flag.participants.all():
            Notification(
                source=request.user,
                target=participant,
                notification_type=Notification.FLAG_PARTICIPANT_JOINED,
                subject=flag).save()
        flag.participants.add(request.user)
        messages.success(request, 'You are now a participant in this flag')
    return redirect


@permission_required('administration.can_resolve_flags', raise_exception=True)
@staff_member_required
@require_POST
def resolve_flag(request, flag_id=None):
    flag = get_object_or_404(Flag, pk=flag_id)
    social = 'administration.can_view_social_applications'
    content = 'administration.can_view_content_applications'
    if not ((request.user.has_perm(social) and
             flag.flag_type == Flag.SOCIAL) or
            (request.user.has_perm(content) and
             flag.flag_type == Flag.CONTENT)):
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
        }, status=403)
    if request.user not in flag.participants.all():
        messages.error(request, 'You must be participating in this flag to '
                       'resolve it')
        return redirect(flag.get_absolute_url())
    resolution = request.POST.get('resolution')
    if resolution is None:
        messages.error(request, 'You must provide a resolution')
        return redirect(flag.get_absolute_url())
    flag.resolution = resolution
    flag.resolved = timezone.now()
    flag.resolved_by = request.user
    flag.save()
    for participant in flag.participants.all():
        if participant != request.user:
            Notification(
                source=request.user,
                target=participant,
                notification_type=Notification.FLAG_RESOLVED,
                subject=flag).save()
    messages.success(request, 'Flag resolved')
    return redirect(reverse('administration:list_participating_flags'))
