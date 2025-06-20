import datetime
import io
from urllib.parse import quote
import zipfile

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import F
from weasyprint import HTML

from apps.core.models import Subject, Group
from apps.tests_app.models import TaskSolution, ResultsCalculator
from apps.tests_management.models import Task, Test
import apps.personal_cards.forms as forms
import apps.personal_cards.models as models
from apps.core.views import ListFiltersMixin


class GroupsListView(ListFiltersMixin, generic.ListView):
    model = Group
    template_name = "personal_cards/groups_list.html"
    context_object_name = "groups"
    filter_fields = ["campus"]
    

class GroupBatchesListView(generic.ListView):
    model = models.CardsBatch
    context_object_name = "batches"
    template_name = "personal_cards/group_batches.html"

    def get_queryset(self):
        group_id = self.kwargs["group_id"]
        return super().get_queryset().filter(group_id=group_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["group"] = Group.objects.get(id=self.kwargs["group_id"])
        context["create_batch_form"] = forms.CreateBatchForm(
            self.request.POST or None
        )
        
        return context


class BatchView(generic.DetailView):
    model = models.CardsBatch
    template_name = "personal_cards/batch.html"
    context_object_name = "batch"


class CreateBatchWithCardsView(generic.View):
    subjects = Subject.objects.all()
    softskills = models.SoftSkill.objects.all()

    @staticmethod
    def create_cards(batch):
        return [
            models.PersonalCard.objects.create(
                batch=batch,
                student=student,
            )
            for student in batch.group.students.all()
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
        group = get_object_or_404(Group, pk=pk)
        form = forms.CreateBatchForm(data=request.POST)

        if form.is_valid():
            with transaction.atomic():
                # создание карточек
                batch = models.CardsBatch.objects.create(
                    group=group, 
                    start_date=form.cleaned_data["start_date"],
                    end_date=form.cleaned_data["end_date"],
                )
                
                cards = self.create_cards(batch=batch)
                
                # создание связанных объектов
                self.create_recommendations(cards)
                self.create_strengths(cards)
                self.create_softskills_marks(cards)
                
            messages.success(request, "Карточки успешно созданы!")
            
        else:
            print(dict(form.errors))
            messages.error(request, f"Ошибки при заполнении формы: {form.errors}")
        
        return redirect(reverse_lazy("personal_cards:group", args=[group.id]))


class DeleteBatchView(generic.View):
    def post(self, request, pk):
        batch = get_object_or_404(models.CardsBatch, pk=pk)
        success_url = reverse_lazy("personal_cards:group", args=[batch.group_id])
        
        batch.delete()
        return redirect(success_url)


class CardConstructorMixin:
    """
    Предоставляет методы для формирования личных карточек.
    Предполагает наличие атрибута self.card
    """

    def _get_written_tests(self):
        """
        Возвращает тесты, написанные от 1 сентября текущего года
        до конца отчетного периода отчёта
        """
        
        card_month = self.card.batch.start_date.month
        card_year = self.card.batch.start_date.year
        studing_year_started = datetime.date(
            card_year if card_month in (9, 10, 11, 12) else card_year - 1,
            9, 1,
        )
        return Test.objects.filter(
            testassign__writing_date__gte=studing_year_started,
            testassign__writing_date__lte=self.card.batch.end_date,
            testassign__group=self.card.student.group
        ).order_by("testassign__writing_date")

    def get_repeat_topics(self):
        """
        Возвращает темы заданий базового уровня с ошибками 
        (не максимальный балл) из тестов, написанных в отчётный период
        """      
        
        solutions_with_mistakes = TaskSolution.objects.filter(
            task__test__in=self._get_written_tests(),
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

    def get_tests_results(self):
        tests_by_subjects = {subject: [] for subject in Subject.objects.all()}

        for test in self._get_written_tests():
            calculator = ResultsCalculator(test, self.card.student)
            
            result = {"test": test, "basic_percent": "-", "reflexive_percent": "-"}
            
            if not calculator.empty_result:
                result["basic_percent"] = calculator.get_total_percent(Task.BASIC)
                if test.with_reflexive_level:
                    result["reflexive_percent"] = calculator.get_total_percent(Task.REFLEXIVE)

            tests_by_subjects[test.subject].append(result)

        return tests_by_subjects

    def get_softskills_marks(self):
        marks_by_skill = {skill: [] for skill in models.SoftSkill.objects.all()}
        marks = (
            models.SoftSkillMark.objects
            .filter(card__student=self.card.student)
            .exclude(mark__isnull=True)
            .order_by("-card__batch__start_date")[:3]
        )

        for mark in marks:
            marks_by_skill[mark.skill].append(mark)
        
        return marks_by_skill

    def get_recommendations(self):
        return {
            rec.subject.name: rec.text for rec in 
            models.PersonalRecommendations.objects.filter(card=self.card)
        }
    
    def get_strengths(self):
        return {
            s.subject.name: s.text for s in 
            models.PersonalStrength.objects.filter(card=self.card)
        }
    
    def get_recommendations_formset(self, post_data=None):
        return forms.RecommendationsFormset(post_data, instance=self.card)
        
    def get_strengths_formset(self, post_data=None):
        return forms.StrengthsFormset(post_data, instance=self.card)
        
    def get_softskills_formset(self, post_data=None):
        return forms.SofskillsFormset(post_data, instance=self.card)
    
    def get_view_context(self):
        """
        Возвращает контекст для использования в CardView:
        неизменяемые данные представлены в виде словарей,
        изменяемые - в виде форм
        """
        return {
            "card": self.card,
            "tests": self.get_tests_results(),
            "repeat_topics": self.get_repeat_topics(),
            "softskills": self.get_softskills_marks(),
            "recommendations_formset": self.get_recommendations_formset(),
            "strengths_formset": self.get_strengths_formset(),
            "softskills_formset": self.get_softskills_formset()
        }
    
    def get_pdf_context(self):
        """
        Возвращает контекст для формирования pdf-документа
        """
        return {
            "card": self.card,
            "tests": self.get_tests_results(),
            "repeat_topics": self.get_repeat_topics(),
            "softskills": self.get_softskills_marks(),
            "recommendations": self.get_recommendations(),
            "strengths": self.get_strengths(),
        }
        
    def get_pdf(self):
        """
        Возвращает pdf-документ в виде последовательности байтов
        """
        html_string = render_to_string(
            template_name="personal_cards/personal_card_pdf.html",
            context=self.get_pdf_context(),
        )
        html = HTML(
            string=html_string,
            base_url=settings.BASE_DIR,
        )
        return html.write_pdf()
        
    def get_filename(self):
        return (
            f"{self.card.student.surname} {self.card.student.name} "
            f"от {self.card.batch.start_date}.pdf"
        )
    
    def get_pdf_filename(self):
        return quote(self.get_filename())
        

class CardConstructor(CardConstructorMixin):
    """
    Самостоятельный класс для отображения карточки
    """
    def __init__(self, card):
        self.card = card
        

class CardView(generic.View, CardConstructorMixin):
    template_name = "personal_card.html"
    
    def dispatch(self, request, *args, **kwargs):
        self.card=models.PersonalCard.objects.get(id=kwargs["card_id"])
        return super().dispatch(request, *args, **kwargs)
        
    def get(self, request, card_id):
        return render(
            request,
            "personal_cards/personal_card.html",
            self.get_view_context(),
        )

    def post(self, request, card_id):
        recommendations_formset = self.get_recommendations_formset(request.POST)
        strengths_formset = self.get_strengths_formset(request.POST)
        softskills_formset = self.get_softskills_formset(request.POST)
        
        if recommendations_formset.is_valid():
            recommendations_formset.save()
        
        if strengths_formset.is_valid():
            strengths_formset.save()
            
        if softskills_formset.is_valid():
            softskills_formset.save()
            
        return redirect(reverse_lazy(
            "personal_cards:card", kwargs={"card_id": card_id}
        ))


class DownloadCardView(generic.View, CardConstructorMixin):
    """
    Возвращает HttpResponse с pdf-файлом и соответствующими заголовками
    """

    template_name = "personal_cards/personal_card_pdf.html"
    
    def get(self, request, *args, **kwargs):
        self.card = get_object_or_404(models.PersonalCard, pk=self.kwargs["pk"])
        
        return HttpResponse(
            content=self.get_pdf(),
            content_type='application/pdf',
            headers={
                "Content-Disposition": f"attachment; filename={self.get_pdf_filename()}"
            }
        )


class DownloadBatchCards(generic.View):
    def get(self, request, pk):
        batch = get_object_or_404(models.CardsBatch, pk=pk)
        
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip:
            for card in batch.cards.all():
                constructor = CardConstructor(card)
                zip.writestr(
                    constructor.get_filename(),
                    constructor.get_pdf(),
                )
        
        filename = f"{batch.group} за {batch.start_date}.zip"
        buffer.seek(0)
        return HttpResponse(
            content=buffer.getvalue(),
            content_type='application/zip',
            headers={
                "Content-Disposition": f"attachment; filename={quote(filename)}"
            }
        )    
            