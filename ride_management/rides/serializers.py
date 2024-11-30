from rest_framework import serializers
from .models import Ride, RideEvent
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = '__all__'

class RideSerializer(serializers.ModelSerializer):
    events = RideEventSerializer(many=True, read_only=True)
    rider = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='rider'))
    driver = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='driver'))
    todays_ride_events = serializers.SerializerMethodField()
    distance = serializers.FloatField(read_only=True)

    class Meta:
        model = Ride
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('rider'):
            raise serializers.ValidationError({"rider": "Rider is required."})
        if not attrs.get('driver'):
            raise serializers.ValidationError({"driver": "Driver is required."})
        return attrs


    def get_todays_ride_events(self, obj):
        from django.utils.timezone import now, timedelta
        today_start = now() - timedelta(days=1)
        return obj.events.filter(timestamp__gte=today_start).count()
