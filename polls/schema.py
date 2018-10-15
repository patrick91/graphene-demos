import graphene

from .models import Poll
from .types import PollType


class PollsQuery(object):
    polls = graphene.List(graphene.NonNull(PollType))

    def resolve_polls(self, info):
        return Poll.objects.all()
