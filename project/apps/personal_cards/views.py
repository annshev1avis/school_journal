import datetime

from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import F

from apps.core.models import Subject, Group
from apps.tests_app.models import TaskSolution, ResultsCalculator
from apps.tests_management.models import TestAssign, Task, Test
import apps.personal_cards.forms as forms
import apps.personal_cards.models as models
from apps.core.views import ListFiltersMixin


class GroupsListView(ListFiltersMixin, generic.ListView):
    model = Group
    template_name = "personal_cards/groups_list.html"
    context_object_name = "groups"
    filter_fields = ["campus"]
    

class GroupView(generic.ListView):
    model = models.PersonalCard
    template_name = "personal_cards/group.html"
    context_object_name = "cards"

    def get_queryset(self):
        group_id = self.kwargs["group_id"]
        return super().get_queryset().filter(student__group_id=group_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = Group.objects.get(id=self.kwargs["group_id"])
        return context


class GroupActiveCardsView(GroupView):
    template_name = "personal_cards/group_active_cards.html"
    
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["create_cards_form"] = forms.CreateCardsForm()
        
        return context


class GroupArchivedCardsView(GroupView):
    template_name = "personal_cards/group_archived_cards.html"
    
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=True)


class CreateCardsView(generic.DetailView):
    model = Group

    subjects = Subject.objects.all()
    softskills = models.SoftSkill.objects.all()

    @staticmethod
    def create_cards(group, start_date, end_date):
        return [
            models.PersonalCard.objects.create(
                student=student,
                start_date=start_date,
                end_date=end_date
            )
            for student in group.students.all()
        ]
        
    def create_recommendations(self, cards):
        recs = [
            models.PersonalRecommendations(card=card, subject=subject)
            for subject in self.subjects
            for card in cards
        ]
        models.PersonalRecommendations.objects.bulk_create(recs)
        
    def create_strengths(self, cards):
        strengths = [
            models.PersonalStrength(card=card, subject=subject)
            for subject in self.subjects
            for card in cards
        ]
        models.PersonalStrength.objects.bulk_create(strengths)
        
    def create_softskills_marks(self, cards):
        marks = [
            models.SoftSkillMark(card=card, skill=skill)
            for card in cards
            for skill in self.softskills
        ]
        models.SoftSkillMark.objects.bulk_create(marks)
            
    def post(self, request, pk):
        group = self.get_object()
        form = forms.CreateCardsForm(data=request.POST)

        if form.is_valid():
            with transaction.atomic():
                # создание карточек
                cards = self.create_cards(
                    group=self.get_object(),
                    start_date=form.cleaned_data["start_date"],
                    end_date=form.cleaned_data["end_date"]
                )
                
                # создание связанных объектов
                self.create_recommendations(cards)
                self.create_strengths(cards)
                
                if form.cleaned_data["add_softskills"]:
                    self.create_softskills_marks(cards)
                
            messages.success(request, "Карточки успешно созданы!")
        else:
            messages.error(request, f"Ошибки при заполнении формы: {form.errors}")
            
        return redirect(reverse_lazy("personal_cards:group", args=[group.id]))


class ArchiveCardsView(generic.DetailView):
    model = Group
    
    def post(self, request, pk):
        (
            models.PersonalCard.objects
            .filter(student__group=self.get_object(), is_archived=False)
            .update(is_archived=True)
        )
        return redirect(reverse_lazy("personal_cards:group", args=[pk]))


class CardView(generic.View):
    template_name = "personal_card.html"
    
    def dispatch(self, request, *args, **kwargs):
        self.card = models.PersonalCard.objects.get(
            id=kwargs["card_id"]
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get_written_tests(self):
        """
        Возвращает тесты, написанные от 1 сентября текущего года
        до конца отчетного периода отчёта
        """
        
        card_month = self.card.start_date.month
        card_year = self.card.start_date.year
        studing_year_started = datetime.date(
            card_year if card_month in (9, 10, 11, 12) else card_year - 1,
            9, 1,
        )
        return Test.objects.filter(
            testassign__writing_date__gte=studing_year_started,
            testassign__writing_date__lte=self.card.end_date,
            testassign__group=self.card.student.group
        ).order_by("testassign__writing_date")
    
    def get_repeat_topics(self):
        """
        Возвращает темы заданий базового уровня с ошибками 
        (не максимальный балл) из тестов, написанных в отчётный период
        """      
        
        solutions_with_mistakes = TaskSolution.objects.filter(
            task__test__in=self.get_written_tests(),
            student=self.card.student,
            task__level=Task.BASIC,
            result__lt=F('task__max_points')
        )

        topics = {}
        for subject in Subject.objects.all():
            topics[subject] = set(
                solutions_with_mistakes
                .filter(task__test__subject=subject)
                .values_list("task__checked_skill", flat=True)
            )
            
        return topics        
    
    def get_tests_by_subjects(self):
        tests_by_subjects = {subject: [] for subject in Subject.objects.all()}

        for test in self.get_written_tests():
            calculator = ResultsCalculator(test, self.card.student)
            
            result = {"test": test, "basic_percent": "-", "reflexive_percent": "-"}
            
            if not calculator.empty_result:
                result["basic_percent"] = calculator.get_total_percent(Task.BASIC)
                if test.with_reflexive_level:
                    result["reflexive_percent"] = calculator.get_total_percent(Task.REFLEXIVE)

            tests_by_subjects[test.subject].append(result)

        return tests_by_subjects
    
    def get(self, request, card_id):
        return render(
            request,
            "personal_cards/personal_card.html",
            {
                "card": self.card,
                "tests_by_subject": self.get_tests_by_subjects(),
                "repeat_topics": self.get_repeat_topics(),
                "recommendations_formset": self.get_recommendations_formset(),
                "strengths_formset": self.get_strengths_formset(), 
            },
        )

    def get_recommendations_formset(self):
        return forms.RecommendationsFormset(
            self.request.POST if self.request.POST else None,
            instance=self.card,
        )
        
    def get_strengths_formset(self):
        return forms.StrengthsFormset(
            self.request.POST if self.request.POST else None,
            instance=self.card,
        )

    def post(self, request, card_id):
        recommendations_formset = self.get_recommendations_formset()
        strengths_formset = self.get_strengths_formset()
        
        if recommendations_formset.is_valid():
            recommendations_formset.save()
        
        if strengths_formset.is_valid():
            strengths_formset.save()
            
        return redirect(reverse_lazy(
            "personal_cards:card", kwargs={"card_id": card_id}
        ))
