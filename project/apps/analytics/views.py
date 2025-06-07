from django.views import generic
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.offline import plot

import apps.analytics.forms as forms
from apps.core.constants import STUDING_MONTHES_DICT
from apps.core.views import ListFiltersMixin
from apps.core.models import Group, Student
from apps.tests_management.models import Test, Task
from apps.tests_app.models import TaskSolution


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


class TestDetailView(generic.DetailView):
    template_name = "analytics/test.html"
    model = Test
    context_object_name = "test"
    
    @staticmethod
    def categorize_result(df_row):
        if df_row["result"] == 0:
            return "не решено"
        
        if df_row["result"] == df_row["task__max_points"]:
            return "решено полностью"
        
        return "решено частично"
    
    @staticmethod
    def style_fig(fig):
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Anonymous Pro", "color": "black"}
        )
    
    @staticmethod
    def get_task_label(df_row):
        return f"""{df_row["task__num"]}.{df_row["task__level"]} {df_row["task__checked_skill"]}"""
    
    def get_tasks_difficulty_plot(self):
        task_solutions = (
            TaskSolution.objects
            .filter(task__test=self.object)
            .values(
                "task", 
                "result", 
                "task__max_points", 
                "task__num", 
                "task__level", 
                "task__checked_skill"
            )
        )
        
        df = (
            pd.DataFrame.from_records(task_solutions)
            .dropna()
            .assign(
                task_label=lambda x: x.apply(self.get_task_label, axis=1),
                result_category=lambda x: x.apply(self.categorize_result, axis=1),
                count=1
            )
            .sort_values(["task__num", "task__level"], ascending=[True, True])
        )
    
        fig = px.bar(
            df,
            x="task_label",
            y="count",
            color="result_category",
            barmode="stack",
            category_orders={
                "task_label": df["task_label"].unique()  # Сохраняем порядок сортировки
            }
        )
        
        fig.update_layout(
            title="Успешность решения заданий",
            xaxis_title="Задачи",
            yaxis_title="Количество решений",
            legend_title_text="Результат",
        )
        self.style_fig(fig)
        
        return plot(fig, output_type="div")
    
    @staticmethod
    def average_solution_percent(group):
        return group["result"].sum() / group["task__max_points"].sum() * 100
    
    def get_groups_average_percent_plot(self):
        task_solutions = (
            TaskSolution.objects.filter(task__test=self.object)
            .values(
                "result", "task__max_points", "task__level",
                "student__group__studing_year", "student__group__letter"
            )
        )
        
        df = pd.DataFrame.from_records(task_solutions)
        df["group_name"] = (
            df["student__group__studing_year"].astype(str) 
            + "-" + df["student__group__letter"]
        )
        grouped = df.groupby(["group_name", "task__level"])
        
        aggregated = grouped.apply(self.average_solution_percent)
        aggregated = aggregated.reset_index()
        aggregated.columns = ["group_name", "task__level", "average_percent"]
        
        fig = px.bar(
            aggregated,
            x="average_percent",
            y="group_name",
            color="task__level",
            orientation='h',
            barmode='group',
            title="Средний процент решения задач по группам и уровням",
            labels={
                "average_percent": "Средний процент решения (%)",
                "student__group": "Группа студентов",
                "task__level": "Уровень сложности"
            }
        )
        
        fig.update_layout(
            xaxis=dict(range=[0, 100]),
        )
        self.style_fig(fig)
        
        return plot(fig, output_type="div")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks_difficulty_plot"] = self.get_tasks_difficulty_plot()
        context["groups_average_percent_plot"] = self.get_groups_average_percent_plot()
        return context
    
    
class GroupDetailView(generic.DetailView):
    template_name = "analytics/group.html"
    model = Group
    context_object_name = "group"

    def get_period_monthes(self, period_form):
        start_month = 1
        end_month = 10
        
        if period_form.is_valid():
            if period_form.cleaned_data["start_month"]:
                start_month = int(period_form.cleaned_data["start_month"])
            if period_form.cleaned_data["end_month"]:
                end_month = int(period_form.cleaned_data["end_month"])
        
        return range(start_month, end_month + 1)

    @staticmethod
    def average_solution_percent(group):
        return group["result"].sum() / group["max_result"].sum() * 100

    @staticmethod
    def get_month_name(df_row):
        return STUDING_MONTHES_DICT[df_row["month"]]

    def get_subjects_plot(self):
        # Исходные данные
        df = pd.DataFrame.from_records(
            TaskSolution.objects.filter(
                task__test__month__in=self.period_monthes,
                student__group=self.object,
            ).values(
                "result", "task__max_points", "task__test__month",
                "task__test__subject__name",
            ),
        ).dropna()
        
        df = df.rename(columns={
            "result": "result",
            "task__max_points": "max_result",
            "task__test__subject__name": "subject",
            "task__test__month": "month",
        })
        
        # Сортировка по числовому месяцу
        df = df.sort_values(by="month")
        df["month_name"] = df.apply(self.get_month_name, axis=1)

        # Группировка и агрегация
        grouped = df.groupby(["subject", "month_name"])
        aggregated = (
            grouped.apply(self.average_solution_percent)
            .reset_index()
        )
        aggregated.columns = ['subject', "month_name", 'average_percent']

        # --- Исправление порядка месяцев ---
        MONTH_ORDER = [
            "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", 
        ]
        
        aggregated["month_name"] = pd.Categorical(
            aggregated["month_name"],
            categories=MONTH_ORDER,
            ordered=True
        )
        aggregated = aggregated.sort_values("month_name")
        # ---

        # Построение графика
        fig = px.line(
            aggregated,
            x="month_name",
            y="average_percent",
            color="subject",
            title="Средний процент выполнения тестов",
            markers=True,
            labels={
                "month_name": "Месяц",
                "average_percent": "Средний процент, %",
                "subject": "Предмет"
            }
        )
        
        fig.update_layout(yaxis_range=[0, 100])
        fig.update_traces(marker=dict(size=12))
        
        return plot(fig, output_type="div")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        period_form = forms.PeriodForm(
            data=self.request.GET if self.request.GET else None
        )
        self.period_monthes = self.get_period_monthes(period_form)
    
        context["period_form"] = period_form
        context["subjects_plot"] = self.get_subjects_plot()
        return context
