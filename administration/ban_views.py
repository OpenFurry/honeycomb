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

# from .forms import (
#     BanForm,
# )
# from .models import (
#     Ban,
# )
# from activitystream.models import Activity
# from usermgmt.models import Notification


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
    # ban = get_object_or_404(Ban, pk=ban_id)
    pass


@staff_member_required
@permission_required('administration.can_lift_bans')
def lift_ban(request, ban_id=None):
    # ban = get_object_or_404(Ban, pk=ban_id)
    pass
