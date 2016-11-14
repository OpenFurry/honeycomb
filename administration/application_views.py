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
)
from .models import (
    Application,
)
from activitystream.models import Activity
from usermgmt.models import Notification


@permission_required('administration.can_list_social_applications',
                     raise_exception=True)
@permission_required('administration.can_list_content_applications',
                     raise_exception=True)
@staff_member_required
def list_all_applications(request):
    """View for listing all applications."""
    if request.GET.get('all'):
        applications = Application.objects.all()
    else:
        applications = Application.objects.filter(resolution='')
    return render(request, 'list_applications.html', {
        'title': 'All applications',
        'applications': applications,
        'tab': 'applications',
        'showing_inactive': request.GET.get('all'),
    })


@permission_required('administration.can_list_social_applications',
                     raise_exception=True)
@staff_member_required
def list_social_applications(request):
    """View for listing only applications for social moderators."""
    query = Q(application_type__in=Application.SOCIAL_TYPES)
    if request.GET.get('all') is None:
        query &= Q(resolution='')
    applications = Application.objects.filter(query)
    return render(request, 'list_applications.html', {
        'title': 'My applications',
        'applications': applications,
        'tab': 'applications',
        'showing_inactive': request.GET.get('all'),
    })


@permission_required('administration.can_list_content_applications',
                     raise_exception=True)
@staff_member_required
def list_content_applications(request):
    """View for only listing applications for content moderators."""
    query = Q(application_type__in=Application.CONTENT_TYPES)
    if request.GET.get('all') is None:
        query &= Q(resolution='')
    applications = Application.objects.filter(query)
    return render(request, 'list_applications.html', {
        'title': 'My applications',
        'applications': applications,
        'tab': 'applications',
        'showing_inactive': request.GET.get('all'),
    })


@login_required
def create_application(request):
    """View for creating a new application."""
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
    """View for viewing a single application."""
    application = get_object_or_404(Application, pk=application_id)

    # Ensure the user can view the application
    application_type = ('social' if application.application_type in
                        Application.SOCIAL_TYPES else 'content')
    pertinent_permission = 'administration.can_view_{}_applications'.format(
        application_type)
    if not(request.user == application.applicant or
            request.user.has_perm(pertinent_permission)):
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
            'additional_error': (
                'Only the owner or moderators who can see {} '
                'applications can see this application.'.format(
                    application_type))
            }, status=403)

    # Display the application
    title = ("<span class=\"glyphicon glyphicon-{}\"></span> {}'s "
             "application to {}").format(
        ({
            'a': 'ok',
            'r': 'remove',
        }[application.resolution] if application.resolution else 'time'),
        application.applicant.profile.get_display_name(),
        application.get_application_type_display().lower())
    Activity.create('adminapplication', 'viewed', application)
    return render(request, 'view_application.html', {
        'application': application,
        'tab': 'applications',
        'title': title,
        'subtitle': (application.get_resolution_display() if
                     application.resolution else 'pending')
    })


@login_required
def list_participating_applications(request):
    """View for listing applications one is participing in."""
    query = (Q(applicant=request.user) | Q(admin_contact=request.user))
    if request.GET.get('all') is None:
        query &= Q(resolution='')
    applications = Application.objects.filter(query)
    return render(request, 'list_applications.html', {
        'title': 'My applications',
        'applications': applications,
        'tab': 'applications',
        'showing_inactive': request.GET.get('all'),
    })


@permission_required('administration.can_resolve_applications',
                     raise_exception=True)
@staff_member_required
@require_POST
def claim_application(request, application_id=None):
    """View for allowing a moderator to claim an application."""
    application = get_object_or_404(Application, pk=application_id)

    # Ensure the user can claim the application
    application_type = ('social' if application.application_type in
                        Application.SOCIAL_TYPES else 'content')
    pertinent_permission = ('administration.can_resolve_{}_'
                            'applications').format(
        application_type)
    if request.user.has_perm(pertinent_permission):
        # Mark the application as claimed
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


@permission_required('administration.can_resolve_applications',
                     raise_exception=True)
@staff_member_required
@require_POST
def resolve_application(request, application_id=None):
    """View for allowing the moderator in charge of the application to resolve
    it as accepted or rejected.
    """
    application = get_object_or_404(Application, pk=application_id)

    # Ensure the user can resolve the application
    if request.user != application.admin_contact:
        messages.error(request, 'Only the admin contact may resolve this '
                       'application.')
        return redirect(application.get_absolute_url())
    application_type = ('social' if application.application_type in
                        Application.SOCIAL_TYPES else 'content')
    pertinent_permission = (
        'administration.can_resolve_{}_applications').format(application_type)
    if not request.user.has_perm(pertinent_permission):
        return render(request, 'permission_denied.html', {
            'title': 'Permission denied',
            'additional_error': (
                'Only moderators who can resolve {} applications may '
                'resolve this application.')
            }, status=403)

    # Ensure the resolution is valid
    resolution = request.POST.get('resolution')
    valid_types = [t[0] for t in Application.RESOLUTION_TYPES]
    if resolution not in valid_types:
        messages.error(request, 'Received invalid resolution type')
        return redirect(application.get_absolute_url())

    # Mark the application as resolved
    application.resolution = resolution
    application.save()
    Notification(
        notification_type=Notification.APPLICATION_RESOLVED,
        source=request.user,
        target=application.applicant,
        subject=application).save()
    messages.success(request, 'The application has been resolved.  Your next '
                     'step <em>must</em> be to take the appropriate action.')
    # TODO redirect to the appropriate page for taking the necessary action.
    # @makyo 2016-11-07 #66
    return redirect(application.get_absolute_url())
