from graphene_django.types import DjangoObjectType

from .models import Choice, Poll


class ChoiceType(DjangoObjectType):
    class Meta:
        model = Choice


class PollType(DjangoObjectType):
    class Meta:
        model = Poll
