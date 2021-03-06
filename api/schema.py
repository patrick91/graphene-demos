import asyncio
import graphene


from polls.schema import PollsQuery
from polls.mutations import PollsMutations
from polls.subscriptions import PollsSubscription


class Query(PollsQuery, graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info, **kwargs):
        return "world"


class Subscription(PollsSubscription, graphene.ObjectType):
    count_seconds = graphene.Int(up_to=graphene.Int())

    async def resolve_count_seconds(root, info, up_to=5):
        i = 0

        while i <= up_to:
            yield i

            i += 1

            await asyncio.sleep(1)


class Mutations(PollsMutations, graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query, mutation=Mutations, subscription=Subscription
)
