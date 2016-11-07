from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from .forms import (
    ApplicationForm,
    BanForm,
    FlagForm,
)
from .models import (
    Application,
    Ban,
    Flag,
)
from usermgmt.models import Notification

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {
        'tab': 'dashboard',
        'title': 'Administration Dashboard',
    })


# Application views
@staff_member_required
@permission_required('administration.can_list_social_applications')
@permission_required('administration.can_list_content_applications')
def list_all_applications(request):
    applications = Application.objects.all()
    return render(request, 'list_applications.html', {
        'title': 'All applications',
        'applications': applications,
        'tab': 'applications'
    })


@staff_member_required
@permission_required('administration.can_list_social_applications')
def list_social_applications(request):
    applications = Application.objects.filter(
        application_type__in=Application.SOCIAL_TYPES)
    return render(request, 'list_applications.html', {
        'title': 'My applications',
        'applications': applications,
        'tab': 'applications'
    })


@staff_member_required
@permission_required('administration.can_list_content_applications')
def list_content_applications(request):
    applications = Application.objects.filter(
        application_type__in=Application.CONTENT_TYPES)
    return render(request, 'list_applications.html', {
        'title': 'My applications',
        'applications': applications,
        'tab': 'applications'
    })


@login_required
def create_application(request):
    form = ApplicationForm()
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.save()
            return redirect(application.get_absolute_url())
    return render(request, 'create_application.html', {
        'form': form,
        'tab': 'applications',
        'title': 'Apply'
    })


@login_required
def view_application(request, application_id=None):
    application = get_object_or_404(Application, pk=application_id)
    print(application.applicant.profile.get_display_name())
    return render(request, 'view_application.html', {
        'application': application,
        'tab': 'applications',
        'title': "{}'s application to {}".format(
            application.applicant.profile.get_display_name(),
            application.get_application_type_display().lower())
    })


@login_required
def list_participating_applications(request):
    applications = Application.objects.filter(Q(applicant=request.user) |
                                              Q(admin_contact=request.user))
    return render(request, 'list_applications.html', {
        'title': 'My applications',
        'applications': applications,
        'tab': 'applications'
    })


@staff_member_required
@permission_required('administration.can_resolve_applications')
@require_POST
def claim_application(request, application_id=None):
    application = get_object_or_404(Application, pk=application_id)
    can_claim = (
        application.application_type in Application.SOCIAL_TYPES and
        request.user.has_perms(
            ['administration.can_list_social_applications'])) or (
        application.application_type in Application.CONTENT_TYPES and
        request.user.has_perms(
            ['administration.can_list_content_applications']))
    if can_claim:
        application.admin_contact = request.user
        application.save()
        messages.success(request, 'Application claimed.')
        Notification(
            notification_type=Notification.APPLICATION_CLAIMED,
            target=application.applicant,
            source=request.user,
            subject=application).save()
    else:
        messages.error(request, 'Cannot claim application; are you the right '
                       'type of moderator?')
    return redirect(application.get_absolute_url())


@staff_member_required
@permission_required('administration.can_resolve_applications')
@require_POST
def resolve_application(request, application_id=None):
    application = get_object_or_404(Application, pk=application_id)
    pass


# Flag views
@staff_member_required
@permission_required('administration.can_list_social_flags')
@permission_required('administration.can_list_content_flags')
def list_all_flags(request):
    pass


@staff_member_required
@permission_required('administration.can_list_social_flags')
def list_social_flags(request):
    pass


@staff_member_required
@permission_required('administration.can_list_content_applications')
def list_content_flags(request):
    pass


@login_required
def create_flag(request):
    pass


@login_required
def view_flag(request, flag_id=None):
    flag = get_object_or_404(Flag, pk=flag_id)
    pass


@login_required
def list_participating_flags(request):
    pass


@staff_member_required
@permission_required('administration.can_list_social_flags')
@permission_required('administration.can_list_content_flags')
def claim_flag(request):
    pass


@staff_member_required
@permission_required('administration.can_resolve_flags')
def resolve_flag(request, flag_id=None):
    flag = get_object_or_404(Flag, pk=flag_id)
    pass


# Ban views
@staff_member_required
@permission_required('administration.can_list_bans')
def list_bans(request):
    pass


@login_required
@permission_required('administration.can_list_bans')
def list_participating_bans(request):
    pass


@staff_member_required
@permission_required('administration.can_ban_users')
def create_ban(request):
    pass


@staff_member_required
@permission_required('administration.can_view_bans')
def view_ban(request, ban_id=None):
    ban = get_object_or_404(Ban, pk=ban_id)
    pass


@staff_member_required
@permission_required('administration.can_lift_bans')
def lift_ban(request, ban_id=None):
    ban = get_object_or_404(Ban, pk=ban_id)
    pass
