import os
from uuid import uuid4

# # https://stackoverflow.com/questions/15140942/django-imagefield-change-file-name-on-upload
# def path_and_rename(path):
#     def wrapper(instance, filename):
#         ext = filename.split('.')[-1]
#         # get filename
#         if instance.pk:
#             filename = '{}.{}'.format(instance.pk, ext)
#         else:
#             # set filename as random string
#             filename = '{}.{}'.format(uuid4().hex, ext)
#         # return the whole path to the file
#         return os.path.join(path, filename)
#     return wrapper

# https://stackoverflow.com/questions/25767787/django-cannot-create-migrations-for-imagefield-with-dynamic-upload-to-value
from django.utils.deconstruct import deconstructible

@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        if instance.pk:
            filename = '{}.{}'.format(instance.pk, ext)
        else:
            filename = '{}.{}'.format(uuid4().hex, ext)
        return os.path.join(self.path, filename)

import os
DEFAULT_IMAGE_URL = 'default.png'

DEFAULT_AVATAR_DIR = 'avatar/'
DEFAULT_AVATAR_URL = os.path.join(DEFAULT_AVATAR_DIR, 'default.png')

path_and_rename_avatar = PathAndRename(DEFAULT_AVATAR_DIR)

DEFAULT_ORG_AVATAR_DIR = 'org_avatar/'
DEFAULT_ORG_AVATAR_URL = os.path.join(DEFAULT_ORG_AVATAR_DIR, 'default.png')

path_and_rename_org_avatar = PathAndRename(DEFAULT_ORG_AVATAR_DIR)

# ====
DEFAULT_TEST_DATA_DIR = 'problems/test_data'
DEFAULT_TEST_DATA_URL = os.path.join(DEFAULT_ORG_AVATAR_DIR, 'default.zip')

path_and_rename_test_zip = PathAndRename(DEFAULT_TEST_DATA_DIR)