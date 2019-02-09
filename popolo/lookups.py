from ajax_select import register, LookupChannel
from .models import Area, Organization, Person


@register('areas')
class AreaLookup(LookupChannel):

    model = Area

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by('name')[:50]

    def format_item_display(self, item):
        return u"<span class='area'>%s</span>" % item.name


@register('organizations')
class OrganizationLookup(LookupChannel):

    model = Organization

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by('name')[:50]

    def format_item_display(self, item):
        return u"<span class='organization'>%s</span>" % item.name


@register('persons')
class PersonLookup(LookupChannel):

    model = Person

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by('name')[:50]

    def format_item_display(self, item):
        return u"<span class='person'>%s</span>" % item.name
