import asyncio
import graphene


class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info, **kwargs):
        return "world"


class Subscription(graphene.ObjectType):
    count_seconds = graphene.Int(up_to=graphene.Int())

    async def resolve_count_seconds(root, info, up_to=5):
        i = 0

        while i <= up_to:
            yield i

            i += 1

            await asyncio.sleep(1)


schema = graphene.Schema(query=Query, subscription=Subscription)
