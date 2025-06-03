from django.views import generic

from apps.core.views import ListFiltersMixin
from apps.core.models import Group
from apps.tests_management.models import Test


class ChooseSectionView(generic.TemplateView):
    template_name = "analytics/choose_section.html"


class TestsListView(ListFiltersMixin, generic.ListView):
    template_name = "analytics/tests_list.html"
    model = Test
    context_object_name = "tests"
    filter_fields = ["subject", "studing_year"]
    

class GroupsListView(ListFiltersMixin, generic.ListView):
    template_name = "analytics/groups_list.html"
    model = Group
    context_object_name = "groups"
    filter_fields = ["campus", "studing_year"]


