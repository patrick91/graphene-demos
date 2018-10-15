from graphql_ws.django_channels import GraphQLSubscriptionConsumer
from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter([path("subscriptions", GraphQLSubscriptionConsumer)])
        )
    }
)
