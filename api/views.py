from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import *
from .serializers import *
from decimal import Decimal

from .serializers import WithdrawSerializer
from .serializers import DepositSerializer
from .serializers import TransferSerializer

import random
import decimal

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import (
    status,
    generics
)
from rest_framework_simplejwt import authentication as authenticationJWT
from .serializers import UserSerializer
from .permissions import IsCreationOrIsAuthenticated
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt import authentication as authenticationJWT

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManagerUserAPiView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsCreationOrIsAuthenticated]

    def get_object(self):
        return self.request.user

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdressView(ModelViewSet):
    queryset = Adress.objects.all()
    serializer_class = AdressSerializer


class UserView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ContactView(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class AccountView(ModelViewSet):
    queryset = Account.objects.all()
    authentication_classes = [authenticationJWT.JWTAuthentication]

    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(
            client_id=self.request.user
        ).order_by('-created_at').distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AccountDetailSerializer
        
        return AccountSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            agency = ''
            number = ''
            balance = 0
            account_type = 'Elit'
            for i in range(8):
                number += str(random.randint(0,9))
            for i in range(4):
                agency += str(random.randint(0,9))
            account = Account(
                client_id=self.request.user,
                account_agency=agency,
                account_number=number,
                account_balance=balance,
                account_type=account_type 
            )
            account.balance = decimal.Decimal(0)
            account.save()

            return Response({'message': 'created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True, url_path='to_withdraw')
    def to_withdraw(self, request, pk=None):
        account = Account.objects.filter(id=pk).first()

        if account:
            serializer_recebed = WithdrawSerializer(data=request.data)
            if serializer_recebed.is_valid():
                valueWithDraw = decimal.Decimal(serializer_recebed.validated_data.get('value'))
                balance = decimal.Decimal(account.account_balance)

                if balance >= valueWithDraw:
                    new_balance = balance - valueWithDraw
                    account.account_balance = new_balance
                    account.save()

                    return Response({"balance": account.account_balance}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': "Insufficient funds"}, status=status.HTTP_403_FORBIDDEN)

        return Response({'message': "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @action(methods=['POST'], detail=True, url_path='deposit')
    def deposit(self, request, pk=None):
        account = Account.objects.filter(id=pk).first()
        serializer_recebed = DepositSerializer(data=request.data)

        if account:
            if serializer_recebed.is_valid():
                deposited_value = decimal.Decimal(serializer_recebed.validated_data.get('value'))
                saldo = decimal.Decimal(account.account_balance)
                novo_saldo = saldo + deposited_value

                account.account_balance = novo_saldo
                account.save()

                return Response({"balance": account.account_balance}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer_recebed.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "Account not found"}, status=status.HTTP_404_NOT_FOUND)


    @action(methods=['POST'], detail=True, url_path='transfer')
    def transfer(self, request, pk=None):
        target_account = get_object_or_404(Account, id=pk)

        source_account = self.request.user.account_set.first()

        transfer_value = Decimal(request.data.get('valor', 0))

        if source_account and target_account:
            if source_account.account_balance >= transfer_value:
                source_account.account_balance = Decimal(str(source_account.account_balance)) - transfer_value

                target_account.account_balance = Decimal(str(target_account.account_balance)) + transfer_value

                source_account.save()
                target_account.save()

                Transfer.objects.create(
                    origin_id_account=source_account,
                    account_id_destination=target_account,
                    value=transfer_value,
                    obs=request.data.get('obs', ''),
                    transfer_type=request.data.get('transfer_type', '')
                )

                return Response({'message': 'Transfer completed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Insufficient balance in home account'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message': 'Accounts not found'}, status=status.HTTP_404_NOT_FOUND) 
        

    @action(methods=['POST'], detail=True, url_path='to_loan')
    def to_loan(self, request, pk=None):
        account = Account.objects.filter(id=pk).first()

        if account:
            serializer = LoanSerializer(data=request.data)

            if serializer.is_valid():
                loan_value = Decimal(serializer.validated_data.get('loan_value'))
                interest_loan= Decimal(serializer.validated_data.get('interest_loan'))
                quantity_parcels = serializer.validated_data.get('loan_quantity_parcelas')
                observation = serializer.validated_data.get('loan_observation', '')

                with transaction.atomic():
                    account.account_balance = float(account.account_balance) + float(loan_value)
                    account.save()

                    Loan.objects.create(
                        account_id=account,
                        loan_value=float(loan_value),
                        interest_loan=float(interest_loan),
                        loan_quantity_parcelas=quantity_parcels,
                        loan_observation=observation
                    )

                return Response({'message': 'Loan completed successfully'}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)


class CardView(ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer


class MovimentationView(ModelViewSet):
    queryset = Movimentation.objects.all()
    serializer_class = MovimentationSerializer

    def get_queryset(self):
        user = self.request.user
        trasfers = Transfer.objects.filter(account_id_origin__client_id=user) | Transfer.objects.filter(account_id_destino__client_id=user)
        withdrawals = Movimentation.objects.filter(movement_type='withdraw', account_id__client_id=user)
        deposits = Movimentation.objects.filter(movement_type='deposit', account_id__client_id=user)

        queryset = trasfers | withdrawals | deposits
        return queryset


class LoanView(ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer


# class InvestimentView(ModelViewSet):
#     queryset = Investiment.objects.all()
#     serializer_class = InvestimentSerializer


class TransferView(ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Extract, Movimentation, Loan
from .serializers import ExtractSerializer

class ExtractView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        loans = Loan.objects.filter(account_id__client_id=user)

        last_data_extract = Extract.objects.filter(account_id__client_id=user).order_by('-created_at').first()

        for loan in loans:
            if not last_data_extract or loan.created_at > last_data_extract.created_at:
                Extract.objects.create(account_id=loan.account_id, type_transition='Loan', value=loan.loan_value)

        exract = Extract.objects.filter(account_id__client_id=user)

        exract_serializaded = ExtractSerializer(exract, many=True).data

        return Response({'extract': exract_serializaded}, status=status.HTTP_200_OK)