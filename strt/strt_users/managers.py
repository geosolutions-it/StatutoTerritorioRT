#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class AppUserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, fiscal_code, email, password=None, **extra_fields):
        if not fiscal_code:
            raise ValueError(_('Il codice fiscale deve essere inserito'))
        if email:
            email = self.normalize_email(email)
        user = self.model(fiscal_code=fiscal_code, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, fiscal_code, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(fiscal_code, email, **extra_fields)

    def create_superuser(self, fiscal_code, password, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(fiscal_code, email, password, **extra_fields)
