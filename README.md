# gRPC-with-Python

---------------------------------------------------------------------------------

## Instale as bibliotecas:
python -m venv venv
venv/scripts/Activate.ps1
pip install django==3.0
pip install djangorestframework
pip install djangogrpcframework
pip install grpcio
pip install grpcio-tools

---------------------------------------------------------------------------------

## Inicie o projeto:
django-admin startproject quickstart
cd quickstart
django-admin startapp account
python manage.py migrate

---------------------------------------------------------------------------------

## Configure o settings.py
Add django_socio_grpc to INSTALLED_APPS, settings module is in tutorial/settings.py:
INSTALLED_APPS = [
    ...
    'django_grpc_framework',
]

---------------------------------------------------------------------------------

## Na pasta principal, juntamente com o manage.py, crie o arquivo account.proto e escreva nele:
syntax = "proto3";

package account;

import "google/protobuf/empty.proto";

service UserController {
    rpc List(UserListRequest) returns (stream User) {}
    rpc Create(User) returns (User) {}
    rpc Retrieve(UserRetrieveRequest) returns (User) {}
    rpc Update(User) returns (User) {}
    rpc Destroy(User) returns (google.protobuf.Empty) {}
}

message User {
    int32 id = 1;
    string username = 2;
    string email = 3;
    repeated int32 groups = 4;
}

message UserListRequest {
}

message UserRetrieveRequest {
    int32 id = 1;
}

---------------------------------------------------------------------------------

## Rode o comando para gerar os arquivos grpc:

python -m grpc_tools.protoc --proto_path=./ --python_out=./ --grpc_python_out=./ ./account.proto

---------------------------------------------------------------------------------

## Define a Serializer na pasta account:
from django.contrib.auth.models import User
from django_grpc_framework import proto_serializers
import account_pb2


class UserProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = User
        proto_class = account_pb2.User
        fields = ['id', 'username', 'email', 'groups']

---------------------------------------------------------------------------------

## Define a services.py na pasta account:
from django.contrib.auth.models import User
from django_grpc_framework import generics
from account.serializers import UserProtoSerializer


class UserService(generics.ModelService):
    """
    gRPC service that allows users to be retrieved or updated.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserProtoSerializer

---------------------------------------------------------------------------------

## Define a services.py na pasta quickstart:

import account_pb2_grpc
from account.services import UserService


urlpatterns = []


def grpc_handlers(server):
    account_pb2_grpc.add_UserControllerServicer_to_server(UserService.as_servicer(), server)

---------------------------------------------------------------------------------

## Rode o Comando para dar run no projeto:

python manage.py grpcrunserver --dev

---------------------------------------------------------------------------------

## Agora podemos acessar nosso serviço a partir do cliente gRPC:

import grpc
import account_pb2
import account_pb2_grpc


with grpc.insecure_channel('localhost:50051') as channel:
    stub = account_pb2_grpc.UserControllerStub(channel)
    for user in stub.List(account_pb2.UserListRequest()):
        print(user, end='')
