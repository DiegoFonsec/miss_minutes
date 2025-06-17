from rest_framework import serializers
from wagtail_dp_tools.csrgenerator.models import CSRGeneratorHistory

class CSRGeneratorHistorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = CSRGeneratorHistory
        fields = [
            'id',
            'user',
            'project_name',
            'common_name',
            'dns_san',
            'ip_san',
            'created_at'
        ]

class CSRGeneratorCreateSerializer(serializers.Serializer):
    project_name = serializers.CharField()
    country = serializers.CharField()
    state = serializers.CharField()
    locality = serializers.CharField()
    org_name = serializers.CharField()
    org_unit = serializers.CharField()
    common_name = serializers.CharField()
    alt_dns = serializers.CharField(required=False, allow_blank=True)
    use_ips = serializers.BooleanField(default=False)
    alt_ips = serializers.CharField(required=False, allow_blank=True)

    email = serializers.EmailField(required=False, allow_blank=True)
    default_bits = serializers.IntegerField(default=2048)
    prompt = serializers.ChoiceField(choices=['no', 'yes'], default='no')
    distinguished_name = serializers.CharField(default='req_distinguished_name')
    req_extensions = serializers.CharField(default='req_ext')