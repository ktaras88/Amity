from rest_framework import serializers


class RequestEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]


class SecurityCodeSerializer(serializers.Serializer):
    security_code = serializers.CharField(min_length=6, max_length=6)

    class Meta:
        fields = ["security_code"]
