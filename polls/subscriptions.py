import uuid
import graphene

import aiopubsub

from .models import Poll
from .types import PollType
from .pubsub import hub


class PollsSubscription(graphene.ObjectType):
    on_poll_updated = graphene.Field(PollType)

    async def resolve_on_poll_updated(root, info):
        subscriber = aiopubsub.Subscriber(hub, str(uuid.uuid4()))

        subscriber.subscribe(aiopubsub.Key("poll", "on_vote"))

        yield Poll.objects.first()

        while True:
            _, message = await subscriber.consume()

            yield message
