import graphene
from graphene_django.forms.mutation import DjangoFormMutation

from .models import Poll
from .forms import VoteForm
from .types import PollType


class Vote(DjangoFormMutation):
    poll = graphene.Field(PollType)

    class Meta:
        form_class = VoteForm

    def resolve_poll(self, info):
        # TODO: use arguments to fetch correct poll
        return Poll.objects.first()


class PollsMutations:
    vote = Vote.Field()
