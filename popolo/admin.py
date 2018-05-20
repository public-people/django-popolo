from django.contrib import admin
try:
    from django.contrib.contenttypes.admin import GenericTabularInline
except ImportError:
    from django.contrib.contenttypes.generic import GenericTabularInline

from popolo import models
from .behaviors import admin as generics
from django.utils.translation import ugettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin
from django import forms
import json


class MembershipInline(admin.StackedInline):
    extra = 0
    model = models.Membership


class PersonForm(forms.ModelForm):

    extra_field = forms.CharField()

    def save(self, commit=True):
        extra_field = self.cleaned_data.get('extra_field', None)
        person = super(PersonForm, self).save(commit=False)
        person.changeReason = json.dumps({
                'source': extra_field,
                'type': 'manual',
            })
        if commit:
            person.save()
        return person

    class Meta:
        model = models.Person
        fields = '__all__'


class PersonAdmin(SimpleHistoryAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'gender', 'birth_date', 'death_date')
        }),
        ('Biography', {
            'classes': ('collapse',),
            'fields': ('summary', 'image', 'biography')
        }),
        ('Honorifics', {
            'classes': ('collapse',),
            'fields': ('honorific_prefix', 'honorific_suffix')
        }),
        ('Demography', {
            'classes': ('collapse',),
            'fields': ('national_identity',)
        }),
        ('Special Names', {
            'classes': ('collapse',),
            'fields': ('family_name', 'given_name', 'additional_name','patronymic_name','sort_name')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('start_date', 'end_date')
        }),
        ('Change reason', {
            'fields': ('extra_field',),
        })
    )
    inlines = generics.BASE_INLINES + [MembershipInline]
    search_fields = (
        'name',
        'family_name',
        'given_name',
        'additional_name',
        'patronymic_name',
    )

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = PersonForm
        return super(PersonAdmin, self).get_form(request, obj, **kwargs)


class OrganizationMembersInline(MembershipInline):
    verbose_name = _("Member")
    verbose_name_plural = _("Members of this organization")
    fk_name = 'organization'


class OrganizationOnBehalfInline(MembershipInline):
    verbose_name = "Proxy member"
    verbose_name_plural = "Members acting on behalf of this organization"
    fk_name = 'on_behalf_of'


class PostAdmin(SimpleHistoryAdmin):
    model = models.Post
    fieldsets = (
        (None, {
            'fields': ('label','role', 'start_date', 'end_date')
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('other_label', 'area', 'organization')
        }),
    )
    inlines = [
            generics.LinkAdmin,generics.ContactDetailAdmin,generics.SourceAdmin
        ]


class OrganizationAdmin(SimpleHistoryAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'founding_date', 'dissolution_date')
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('summary', 'image', 'description')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('classification','start_date', 'end_date')
        }),
    )
    inlines = generics.BASE_INLINES + [OrganizationMembersInline,OrganizationOnBehalfInline]
    search_fields = (
        'name',
    )


admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Organization, OrganizationAdmin)
