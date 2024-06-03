from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import UserSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

@api_view(['POST'])
def login(request):

    user = get_object_or_404(User, email=request.data['email'])

    if not user.check_password(request.data['password']):
        return Response(
            {"error": "Invalid password"},
            status=status.HTTP_400_BAD_REQUEST
        )

    token, created = Token.objects.get_or_create(user=user)

    serializer = UserSerializer(instance=user)

    return Response({"token": token.key, "user": serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        # GUARDO UNA VEZ EN LA BASE DE DATOS
        serializer.save()
        user = User.objects.get(username=serializer.data['username'])
        # BUSCO EL USER Y ENCRIPTO LA PASSWORD CON SET_PASSWORD PARA GUARDAR NUEVAMENTE EN LA BASE DE DATOS
        user.set_password(serializer.data['password'])
        user.save()

        # CREO EL TOKEN DEL USUARIO GUARDADO
        token = Token.objects.create(user=user)

        # DEVUELVO EL TOKEN
        return Response(
            {'token': token.key, 'user': serializer.data},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# AUTHENTICATION_CLASSES, METODO QUE VA A UTILIZAR PARA AUTENTICARSE
# PERMISSION_CLASSES, DICE QUE SI LA RUTA ESTA PROTEGIDA O NO
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    print(request.user)

    serializer = UserSerializer(request.user)


    # return Response("You are login with {}".format(request.user.username), status=status.HTTP_200_OK)
    return Response(serializer.data, status=status.HTTP_200_OK)