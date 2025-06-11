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


def style_fig(fig):
    """Стилизация графика."""
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Anonymous Pro", "color": "black"},
        margin=dict(l=20, r=20, t=40, b=20),
        title={
            "font": {
                "weight": 700,
                "size": 18
            }
        }
    )
    # Настройки осей (должны быть после update_layout)
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor="lightgray",
        gridcolor="#e0e0e0"  # Светло-серая сетка
    )
    
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor="lightgray",
        gridcolor="#e0e0e0"
    )


class TestDetailView(generic.DetailView):
    template_name = "analytics/test.html"
    model = Test
    context_object_name = "test"
    
    @staticmethod
    def categorize_result(df_row):
        """Категоризация результата решения задачи."""
        if df_row["result"] == 0:
            return "Не решено"
        if df_row["result"] == df_row["task__max_points"]:
            return "Полное решение"
        
        return "Частичное решение"
    
    @staticmethod
    def get_task_label(df_row):
        """Формирование читаемой метки задачи."""
        return f"{df_row['task__num']}.{df_row['task__level']} {df_row['task__checked_skill']}"
    
    def get_tasks_difficulty_plot(self):
        """Построение диаграммы успешности решения задач."""
        task_solutions = (
            TaskSolution.objects
            .filter(task__test=self.object)
            .exclude(result__isnull=True)
        )
        
        if not task_solutions.exists():
            return None
        
        # формируем DataFrame
        values = [
            "result", "task__max_points", 
            "task__num", "task__level", "task__checked_skill"
        ]
        df = pd.DataFrame.from_records(task_solutions.values(*values))
        df = df.assign(
            task_label=lambda x: x.apply(self.get_task_label, axis=1),
            result_category=lambda x: x.apply(self.categorize_result, axis=1)
        )
        df = df.sort_values(["task__num", "task__level"], ascending=[True, True])

        
        # группировка и аггрегация
        result = (
            df.groupby(['task_label', 'result_category'])
            .size()
            .reset_index()
        )
        result.columns = ["task_label", "result_category", "size"]
        
        # формирование графика
        categories_order = ["Не решено", "Частичное решение", "Полное решение"]
        fig = px.bar(
            result,
            x="task_label",
            y="size",
            color="result_category",
            barmode="stack",
            category_orders={
                "task_label": df["task_label"].unique(),
                "result_category": categories_order
            },
            color_discrete_map={
                "Не решено": "#ef553b",
                "Частичное решение": "#636efa",
                "Полное решение": "#00cc96"
            }
        )
        
        fig.update_layout(
            title={
                'text': "Успешность решения заданий",
            },
            xaxis_title="Задачи",
            yaxis_title="Количество решений",
            legend_title_text="",
            hovermode="x unified"
        )
        
        # Улучшаем отображение подписей
        fig.update_xaxes(tickangle=-45)
        fig.update_traces(hovertemplate="%{y}")
        
        style_fig(fig)
        
        return plot(fig, output_type="div")
    
    def get_groups_average_percent_plot(self):
        queryset = (
            TaskSolution.objects
            .filter(task__test=self.object)
            .exclude(result__isnull=True)
        )
        if not queryset.exists():
            return None
        
        # создание dataframe
        values = [
            "result", "task__max_points", "task__level",
            "student__group__studing_year", "student__group__letter"
        ]
        df = pd.DataFrame.from_records(queryset.values(*values))
        df.columns = ["result", "max_result", "task_level", "group_year", "group_letter"]
        df["group_name"] = df["group_year"].astype(str) + "-" + df["group_letter"]
        
        # группировка и аггрегация
        grouped = df.groupby(["group_name", "task_level"]).agg(
            total_result=("result", "sum"),
            total_max=("max_result", "sum")
        )
        grouped["avg_percent"] = grouped["total_result"] / grouped["total_max"] * 100
        result = grouped.reset_index()
        
        fig = px.bar(
            result,
            x="avg_percent",
            y="group_name",
            color="task_level",
            orientation='h',
            barmode='group',
            title="Средний процент решения задач по группам и уровням",
            labels={
                "avg_percent": "Средний процент решения (%)",
                "group_name": "Класс",
                "task_level": "Уровень сложности"
            }
        )
        
        fig.update_layout(
            xaxis=dict(range=[0, 100]),
        )
        style_fig(fig)
        
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

    def get_subjects_plot(self):
        # извлечение данных
        queryset = TaskSolution.objects.filter(
            student__group=self.object,
            task__test__month__in=self.period_monthes,
        ).exclude(result__isnull=True)
        if not queryset.exists():
            return None
    
        # формирование dataframe
        values = [
            "result", "task__max_points", "task__test__month",
            "task__test__subject__name"
        ]
        df = pd.DataFrame.from_records(queryset.values(*values))
        df.columns = ["result", "max_result", "month", "subject"]
        df["month_name"] = df["month"].map(
            lambda x: STUDING_MONTHES_DICT.get(x, "Неизвестный месяц")
        )
        
        # группировка и агрегация
        grouped = df.groupby(["subject", "month_name"]).agg(
            total_result=("result", "sum"),
            total_max=("max_result", "sum")
        )
        grouped["avg_percent"] = grouped["total_result"] / grouped["total_max"] * 100
        result = grouped.reset_index()
        
        # исправление порядка месяцев 
        result["month_name"] = pd.Categorical(
            result["month_name"],
            categories=list(STUDING_MONTHES_DICT.values()),
            ordered=True
        )
        result = result.sort_values("month_name")

        # Построение графика
        fig = px.line(
            result,
            x="month_name",
            y="avg_percent",
            color="subject",
            title="Средний процент выполнения тестов",
            markers=True,
            labels={
                "month_name": "Месяц",
                "avg_percent": "Средний процент, %",
                "subject": "Предмет"
            }
        )
        
        fig.update_layout(yaxis_range=[0, 100]) # подпись y-оси от 0 до 100
        fig.update_traces(marker=dict(size=12)) # добавление точечек
        
        style_fig(fig)
        
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
