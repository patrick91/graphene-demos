from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .base import BaseConnectionContext
from graphql.execution.executors.asyncio import AsyncioExecutor
from .base import BaseSubscriptionServer
from .constants import GQL_CONNECTION_ACK, GQL_CONNECTION_ERROR, GQL_COMPLETE
from graphene_django.settings import graphene_settings
from inspect import isawaitable
from asyncio import ensure_future

from .observable_aiter import setup_observable_extension


setup_observable_extension()


class DjangoChannelConnectionContext(BaseConnectionContext):
    def __init__(self, send_json, close, request_context):
        self.send_json = send_json
        self.close = close
        self.operations = {}
        self.request_context = request_context

    async def send(self, data):
        await self.send_json(data)

    async def close(self, reason):
        await self.close()


class DjangoChannelSubscriptionServer(BaseSubscriptionServer):
    def get_graphql_params(self, connection_context, payload):
        params = {
            "request_string": payload.get("query"),
            "variable_values": payload.get("variables"),
            "operation_name": payload.get("operationName"),
            "context_value": connection_context.request_context,
        }

        return dict(params, return_promise=True, executor=AsyncioExecutor())

    async def handle(self, message, connection_context):
        ensure_future(self.on_message(connection_context, message))

    async def send_message(
        self, connection_context, op_id=None, op_type=None, payload=None
    ):
        message = {}
        if op_id is not None:
            message["id"] = op_id
        if op_type is not None:
            message["type"] = op_type
        if payload is not None:
            message["payload"] = payload

        assert message, "You need to send at least one thing"
        return await connection_context.send(message)

    async def on_open(self, connection_context):
        pass

    async def on_connect(self, connection_context, payload):
        pass

    async def on_connection_init(self, connection_context, op_id, payload):
        try:
            await self.on_connect(connection_context, payload)
            await self.send_message(
                connection_context, op_type=GQL_CONNECTION_ACK
            )

        except Exception as e:
            await self.send_error(
                connection_context, op_id, e, GQL_CONNECTION_ERROR
            )
            await connection_context.close(1011)

    async def on_start(self, connection_context, op_id, params):
        # import pdb; pdb.set_trace()
        execution_result = self.execute(
            connection_context.request_context, params
        )

        if isawaitable(execution_result):
            execution_result = await execution_result

        if not hasattr(execution_result, "__aiter__"):
            await self.send_execution_result(
                connection_context, op_id, execution_result
            )
        else:
            iterator = await execution_result.__aiter__()
            connection_context.register_operation(op_id, iterator)
            async for single_result in iterator:
                if not connection_context.has_operation(op_id):
                    break
                await self.send_execution_result(
                    connection_context, op_id, single_result
                )
            await self.send_message(connection_context, op_id, GQL_COMPLETE)

    async def on_close(self, connection_context):
        remove_operations = list(connection_context.operations.keys())
        for op_id in remove_operations:
            self.unsubscribe(connection_context, op_id)

    async def on_stop(self, connection_context, op_id):
        self.unsubscribe(connection_context, op_id)


class GraphQLSubscriptionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept("graphql-ws")
        self.connection_context = DjangoChannelConnectionContext(
            self.send_json, self.close, self.scope
        )
        self.subscription_server = DjangoChannelSubscriptionServer(
            graphene_settings.SCHEMA
        )
        self.subscription_server.on_open(self.connection_context)

    async def receive_json(self, content):
        if hasattr(self, "subscription_server"):
            await self.subscription_server.handle(
                content, self.connection_context
            )
