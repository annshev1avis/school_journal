from django.views import generic
import pandas as pd
import plotly.express as px
from plotly.offline import plot

from apps.core.views import ListFiltersMixin
from apps.core.models import Group
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
