from django.contrib.auth.models import User
from django_grpc_framework import generics, proto_serializers
import account_pb2
import account_pb2_grpc


class UserProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = User
        proto_class = account_pb2.User
        fields = ['id', 'username', 'email']


class UserService(generics.ModelService):
    queryset = User.objects.all()
    serializer_class = UserProtoSerializer


urlpatterns = []
def grpc_handlers(server):
    account_pb2_grpc.add_UserControllerServicer_to_server(UserService.as_servicer(), server)
