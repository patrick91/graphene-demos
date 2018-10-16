import graphene
from graphene_django.forms.mutation import DjangoFormMutation

from .models import Poll, Choice
from .forms import VoteForm
from .types import PollType


class Vote(DjangoFormMutation):
    poll = graphene.Field(PollType)

    class Meta:
        form_class = VoteForm

    def resolve_poll(self, info):
        # TODO: use arguments to fetch correct poll
        return Poll.objects.first()


class CreatePoll(graphene.Mutation):
    poll = graphene.Field(PollType)

    class Arguments:
        question = graphene.String(required=True)
        choices = graphene.List(graphene.String, required=True)

    def mutate(self, info, question, choices):
        poll = Poll.objects.create(question=question)

        for choice in choices:
            Choice.objects.create(poll=poll, choice_text=choice)

        return CreatePoll(poll)


class PollsMutations:
    vote = Vote.Field()
    create_poll = CreatePoll.Field()
