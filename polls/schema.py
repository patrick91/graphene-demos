import graphene

from .models import Poll
from .types import PollType


class PollsQuery:
    polls = graphene.List(graphene.NonNull(PollType))
    poll = graphene.Field(PollType, id=graphene.ID())

    def resolve_polls(self, info):
        return Poll.objects.all()

    def resolve_poll(self, info, id):
        return Poll.objects.get(pk=id)
