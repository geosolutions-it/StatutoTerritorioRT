#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import (AppUser, Organization, OrganizationType,
                     UserMembership, MembershipType)
from django.contrib.auth.models import Group, User


class OrganizationModelAdmin(admin.ModelAdmin):
    model = Organization
    list_display = ['name', 'code', 'description', 'type']
    search_fields = ['name', 'code', 'description', 'type']
    list_filter = ['name', 'code', 'description', 'type']

class OrganizationTypeModelAdmin(admin.ModelAdmin):
    model = OrganizationType
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code', 'description']
    list_filter = ['name', 'code', 'description']

class MembershipTypeModelAdmin(admin.ModelAdmin):
    model = MembershipType
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code', 'description']
    list_filter = ['name', 'code', 'description']

# class UserMembershipModelAdmin(admin.ModelAdmin):
#     model = UserMembership
#     search_fields = ('code', 'name', 'description')
#     ordering = ('name', 'code')
#     filter_horizontal = ('permissions',)


# admin.site.unregister(User)
admin.site.register(AppUser, UserAdmin)

# admin.site.unregister(Group)
admin.site.register(UserMembership, GroupAdmin)

admin.site.register(Organization, OrganizationModelAdmin)
admin.site.register(OrganizationType, OrganizationTypeModelAdmin)
admin.site.register(MembershipType, MembershipTypeModelAdmin)
