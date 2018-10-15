from django.urls import path

from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

from .views import graphiql


urlpatterns = [
    path("graphiql/", graphiql),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
