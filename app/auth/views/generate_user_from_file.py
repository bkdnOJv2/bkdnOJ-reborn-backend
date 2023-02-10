"""
    generate_user_from_file view for auth module
"""

import csv
import io
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from userprofile.models import UserProfile
from organization.models import Organization
from ..serializers import RegisterSerializer

User = get_user_model()

__all__ = [
    'generate_user_from_file'
]

# FILE_FORMAT = {
#     'user_attributes': {
#         'username': {
#             'required': True,
#         },
#         'password': {
#             'required': False,
#         },
#         'first_name': {
#             'required': False,
#         },
#         'last_name': {
#             'required': False,
#         },
#         'email': {
#             'required': False,
#         },
#     },
#     'config': {
#         'encoding': 'utf-8',
#     }
# }


@api_view(['OPTIONS', 'POST'])
def generate_user_from_file(request):
    """
        Receives a CSV file (formdata, key=file) with format as
        described (call OPTIONS for more info).
        Generate a list of users based on values described.
        Only staff above can call.
    """

    def badreq(msg):
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    if not user.is_staff:
        raise PermissionDenied

    # if request.method == 'OPTIONS':
    #     return Response(FILE_FORMAT, status=status.HTTP_200_OK)

    if request.FILES.get('file') is None:
        return badreq({"detail": "No file named 'file' attached."})

    file = request.FILES['file'].read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(file))

    many_data = list(reader)

    with transaction.atomic():
        for i, data in enumerate(many_data):
            pwd = None
            if 'password' in data.keys():
                pwd = data['password']
            else:
                pwd = get_random_string(length=16)
            data['password'] = data['password_confirm'] = pwd
            many_data[i] = data

        ser = RegisterSerializer(data=many_data, many=True)
        if not ser.is_valid():
            return badreq({'detail': "Cannot create some users.", 'errors': ser.errors})

        users = ser.save()

        # Post value assignment
        profiledata = {}
        for i, data in enumerate(many_data):
            profiledatapoint = {}
            if 'display_name' in data:
                profiledatapoint['display_name'] = data['display_name']
            if 'organization' in data:
                orgslug = data['organization'].upper()
                try:
                    org = Organization.objects.get(slug=orgslug)
                    profiledatapoint['organization'] = org
                except Organization.DoesNotExist:
                    data['organization'] = ''
                    profiledatapoint['organization'] = None
            profiledata[data['username']] = profiledatapoint

        for user in users:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profiledatapoint = profiledata[user.username]
            if profiledatapoint.get('display_name', False):
                profile.username_display_override = profiledatapoint.get(
                    'display_name')
            if profiledatapoint.get('organization', False):
                profile.organizations.add(
                    profiledatapoint.get('organization'))
                profile.display_organization = profiledatapoint.get(
                    'organization')
            profile.first_name = user.first_name
            profile.last_name = user.last_name
            profile.save()

    for data in many_data:
        data.pop('password_confirm', None)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=many_data[0].keys())
    writer.writeheader()
    writer.writerows(many_data)
    return Response(output.getvalue(), status=status.HTTP_201_CREATED)
