from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('index/', views.index, name='index'),
    path('problem_set/', views.probelem_set, name='problem_set'),
    path('problems/<int:prob_id>/', views.problems, name='problems'),
    # path('problems/<int:prob_id>/run_solution/', views.run_solution, name='run_solution'),
    # path('run_solutions2/', views.run_solutions2, name='run_solutions2'),
    path('add_problem/', views.add_problem, name='add_problem'),
    path('edit_problem/<int:prob_id>/', views.edit_problem, name='edit_problem'),
    path('delete_problem/<int:prob_id>/', views.delete_problem, name='delete_problem'),
    path('add_testcase/<int:prob_id>/', views.add_testcase, name='add_testcase'),
    path('problems/run_solution_react/', views.run_solution_react, name='run_solution_react'),
    path('random_sprint/', views.random_sprint, name='random_sprint'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('leaderboard_page/', views.leaderboard_page, name='leaderboard_page'),
    path('top_problems/', views.top_problems, name='top_problems'),
    path('top_problems_page/', views.top_problems_page, name='top_problems_page'),
    path('test_cases/<int:prob_id>', views.test_cases, name='test_cases'),
    path('delete_testcase/<int:tc_id>', views.delete_testcase, name='delete_testcase'),
    path('submissions/', views.submissions, name='submissions'),
]