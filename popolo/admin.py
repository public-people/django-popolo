from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdminStackedInline
from django.contrib import admin
from popolo import models
from .behaviors import admin as generics
from django.utils.translation import ugettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin
from django import forms
import json


class MembershipInline(AjaxSelectAdminStackedInline):
    extra = 0
    model = models.Membership

    form = make_ajax_form(models.Membership, {
        'person': 'persons',
        'area': 'areas',
        'on_behalf_of': 'organizations',
        'organization': 'organizations',
    })


class PersonForm(forms.ModelForm):
    change_reason_help = ("This should be a reference to a URL you place in a "
                          "new Source you add for for this person from "
                          "http://archive.org/web Save Page Now, showing the "
                          "archived URL of a page which serves as a reference "
                          "for the change you're making.")
    change_reason = forms.CharField(max_length=77, help_text=change_reason_help)

    class Meta:
        model = models.Person
        fields = '__all__'

    def save(self, commit=True):
        change_reason = self.cleaned_data.get('change_reason')
        person = super(PersonForm, self).save(commit=False)
        person.changeReason = json.dumps({
                'source': change_reason,
                'type': 'manual',
            })
        if commit:
            person.save()
        return person


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
            'fields': ('change_reason',),
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

    def save_related(self, request, form, formsets, change):
        change_reason = form.cleaned_data.get('change_reason')
        for formset in formsets:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.changeReason = json.dumps({
                    'source': change_reason,
                    'type': 'manual',
                })
        super(PersonAdmin, self).save_related(request, form, formsets, change)


class OrganizationMembersInline(MembershipInline):
    verbose_name = _("Member")
    verbose_name_plural = _("Members of this organization")
    fk_name = 'organization'


class OrganizationOnBehalfInline(MembershipInline):
    verbose_name = "Proxy member"
    verbose_name_plural = "Members acting on behalf of this organization"
    fk_name = 'on_behalf_of'


class PostForm(forms.ModelForm):
    change_reason_help = ("This should be a reference to a URL you place in a "
                          "new Source you add for for this post from "
                          "http://archive.org/web Save Page Now, showing the "
                          "archived URL of a page which serves as a reference "
                          "for the change you're making.")
    change_reason = forms.CharField(max_length=77, help_text=change_reason_help)

    class Meta:
        model = models.Post
        fields = '__all__'

    def save(self, commit=True):
        change_reason = self.cleaned_data.get('change_reason')
        post = super(PostForm, self).save(commit=False)
        post.changeReason = json.dumps({
                'source': change_reason,
                'type': 'manual',
            })
        if commit:
            post.save()
        return post


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
        ('Change reason', {
            'fields': ('change_reason',),
        })
    )
    inlines = [
            generics.LinkAdmin,generics.ContactDetailAdmin,generics.SourceAdmin
        ]

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = PostForm
        return super(PostAdmin, self).get_form(request, obj, **kwargs)

    def save_related(self, request, form, formsets, change):
        change_reason = form.cleaned_data.get('change_reason')
        for formset in formsets:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.changeReason = json.dumps({
                    'source': change_reason,
                    'type': 'manual',
                })
        super(PostAdmin, self).save_related(request, form, formsets, change)


class OrganizationForm(forms.ModelForm):
    change_reason_help = ("This should be a reference to a URL you place in a "
                          "new Source you add for for this organization from "
                          "http://archive.org/web Save Page Now, showing the "
                          "archived URL of a page which serves as a reference "
                          "for the change you're making.")
    change_reason = forms.CharField(max_length=77, help_text=change_reason_help)

    class Meta:
        model = models.Organization
        fields = '__all__'

    def save(self, commit=True):
        change_reason = self.cleaned_data.get('change_reason')
        organization = super(OrganizationForm, self).save(commit=False)
        organization.changeReason = json.dumps({
                'source': change_reason,
                'type': 'manual',
            })
        if commit:
            organization.save()
        return organization


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
        ('Change reason', {
            'fields': ('change_reason',),
        })
    )
    inlines = generics.BASE_INLINES + [OrganizationMembersInline,OrganizationOnBehalfInline]
    search_fields = (
        'name',
    )

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = OrganizationForm
        return super(OrganizationAdmin, self).get_form(request, obj, **kwargs)

    def save_related(self, request, form, formsets, change):
        change_reason = form.cleaned_data.get('change_reason')
        for formset in formsets:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.changeReason = json.dumps({
                    'source': change_reason,
                    'type': 'manual',
                })
        super(OrganizationAdmin, self).save_related(request, form, formsets, change)


class AreaAdmin(SimpleHistoryAdmin):
    pass

admin.site.register(models.Area, AreaAdmin)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Organization, OrganizationAdmin)
