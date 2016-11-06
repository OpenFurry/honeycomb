from django.db.models import Q


def filters_for_authenticated_user(reader):
    """Gets submission filters for an authenticated user.

    Args:
        reader: the user to consider when filtering submissions

    Returns:
        A query object to be used in `Submission.objects.filter`
    """
    # Start with hidden status
    query = Q(hidden=False)

    # Add adult rating status
    if not reader.profile.can_see_adult_submissions:
        query &= Q(adult_rating=False)

    # Add blocked user status
    query &= (~Q(owner__id__in=[x.id for x in reader.blocked_by.all()]))

    # Add group restrictions
    query &= (Q(restricted_to_groups=False) |
              (Q(restricted_to_groups=True) &
               Q(allowed_groups__in=reader.friendgroup_set.all())))

    # Shortcut to allow authors all access
    query = Q(owner=reader) | query
    return query


def filters_for_anonymous_user():
    """Gets submission filters for an anonymous user.

    Returns:
        A query object to be used in `Submission.objects.filter`
    """
    # Start with hidden status
    query = Q(hidden=False)

    # Add adult rating status
    query &= Q(adult_rating=False)

    # Add group restrictions
    query &= Q(restricted_to_groups=False)

    return query
