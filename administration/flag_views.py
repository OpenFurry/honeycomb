from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
# from django.contrib import messages
# from django.db.models import Q
# from django.shortcuts import (
#     get_object_or_404,
#     redirect,
#     render,
# )
from django.views.decorators.http import require_POST

# from .forms import (
#     FlagForm,
# )
# from .models import (
#     Flag,
# )
# from activitystream.models import Activity
# from usermgmt.models import Notification


@permission_required('administration.can_list_social_flags',
                     raise_exception=True)
@permission_required('administration.can_list_content_flags',
                     raise_exception=True)
@staff_member_required
def list_all_flags(request):
    pass


@permission_required('administration.can_list_social_flags',
                     raise_exception=True)
@staff_member_required
def list_social_flags(request):
    pass


@permission_required('administration.can_list_content_applications',
                     raise_exception=True)
@staff_member_required
def list_content_flags(request):
    pass


@login_required
def create_flag(request):
    pass


@login_required
def view_flag(request, flag_id=None):
    # flag = get_object_or_404(Flag, pk=flag_id)
    pass


@login_required
def list_participating_flags(request):
    pass


@permission_required('administration.can_list_social_flags',
                     raise_exception=True)
@permission_required('administration.can_list_content_flags',
                     raise_exception=True)
@staff_member_required
@require_POST
def claim_flag(request, flag_id=None):
    # flag = get_object_or_404(Flag, pk=flag_id)
    pass


@permission_required('administration.can_resolve_flags', raise_exception=True)
@staff_member_required
@require_POST
def resolve_flag(request, flag_id=None):
    # flag = get_object_or_404(Flag, pk=flag_id)
    pass
