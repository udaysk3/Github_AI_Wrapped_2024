from rest_framework import serializers
from .models import GithubUser, GithubStats, GeneratedArt

class GithubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubUser
        fields = '__all__'

class GithubStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubStats
        fields = '__all__'

class GeneratedArtSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedArt
        fields = '__all__'