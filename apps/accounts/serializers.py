from rest_framework import serializers


class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token.
    """
    accessToken = serializers.CharField(allow_blank=False, trim_whitespace=True, )


class PageDetailsSerializer(serializers.Serializer):
    about = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    emails = serializers.EmailField(allow_null=True, allow_blank=True, required=False)
    website = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.IntegerField(required=False, allow_null=True)
