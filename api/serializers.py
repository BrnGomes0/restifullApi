from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers
from .models import *


class AdressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adress
        fields = '__all__'
        many = True


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name', 'last_name', 'cpf', 'created_at', 'url_image']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 6},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def updated(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()

        return user

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        many = True


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_agency', 'account_number', 'account_balance', 'account_type']
        read_only_fields = ['account_number', 'account_balance']


class AccountDetailSerializer(serializers.ModelSerializer):
    class Meta(AccountSerializer.Meta):   
        fields = ['id', 'account_balance', 'account_type', 'created_at',]
        read_only_fields = AccountSerializer.Meta.read_only_fields + ['id', 'account_balance', 'account_type', 'created_at',]


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'
        many = True


class MovimentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimentation
        fields = '__all__'
        many = True


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'
        many = True


# class InvestimentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Investiment
#         fields = '__all__'
#         many = True


class DepositSerializer(serializers.Serializer):
    value = serializers.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        fields = ['value']


class WithdrawSerializer(serializers.Serializer):
    value = serializers.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        fields = ['value']


class TransferSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Transfer
        fields = ['origin_id_account', 'account_id_destination', 'value', 'obs', 'type_transfer']


class ExtractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extract
        fields = '__all__'