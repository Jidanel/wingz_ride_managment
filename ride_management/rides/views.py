from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import RideSerializer, RideEventSerializer
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.db.models import F, Func, Value, FloatField, Prefetch
from django.urls import reverse
from .forms import *
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin


class RidePagination(PageNumberPagination):
    page_size = 10



class Distance(Func):
    """
    Calcul de la distance entre deux points GPS en utilisant une fonction SQL native.
    """
    function = 'ST_Distance_Sphere'
    template = "%(function)s(POINT(%(x1)s, %(y1)s), POINT(%(x2)s, %(y2)s))"

from django.db import connection
import math

class RideViewSet(LoginRequiredMixin, ModelViewSet):
    queryset = Ride.objects.select_related('rider', 'driver').prefetch_related(
        Prefetch(
            'events',
            queryset=RideEvent.objects.filter(timestamp__gte=now() - timedelta(days=1)),
            to_attr='todays_ride_events'
        )
    )
    serializer_class = RideSerializer
    pagination_class = RidePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self.request.user, 'role', None) != 'admin':
            raise PermissionDenied("Only admins can access this resource.")

        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        email = self.request.query_params.get('email')
        order_by = self.request.query_params.get('order_by')
        lat = self.request.query_params.get('latitude')
        lng = self.request.query_params.get('longitude')

        if status:
            queryset = queryset.filter(status=status)
        if email:
            queryset = queryset.filter(rider__email=email)

        if order_by == 'pickup_time':
            queryset = queryset.order_by('start_time')
        elif order_by == 'distance' and lat and lng:
            # Vérifiez le backend de la base de données
            if connection.vendor == 'sqlite':
                # Calcul de la distance en Python pour SQLite
                lat, lng = float(lat), float(lng)

                def calculate_distance(ride):
                    # Convertir les coordonnées en radians
                    ride_lat = math.radians(ride.pickup_latitude)
                    ride_lng = math.radians(ride.pickup_longitude)
                    ref_lat = math.radians(lat)
                    ref_lng = math.radians(lng)

                    # Formule Haversine
                    dlat = ref_lat - ride_lat
                    dlng = ref_lng - ride_lng
                    a = math.sin(dlat / 2) ** 2 + math.cos(ride_lat) * math.cos(ref_lat) * math.sin(dlng / 2) ** 2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                    return 6371 * c  # Rayon moyen de la Terre en km

                for ride in queryset:
                    ride.distance = calculate_distance(ride)
                queryset = sorted(queryset, key=lambda ride: ride.distance)
            else:
                # Utiliser ST_Distance_Sphere pour les bases de données avec prise en charge géospatiale
                queryset = queryset.annotate(
                    distance=Distance(
                        x1=F('pickup_longitude'),
                        y1=F('pickup_latitude'),
                        x2=Value(float(lng)),
                        y2=Value(float(lat)),
                        output_field=FloatField()
                    )
                ).order_by('distance')

        return queryset

class RideEventViewSet(LoginRequiredMixin, ModelViewSet):
    queryset = RideEvent.objects.all()
    serializer_class = RideEventSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class TripDurationReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        query = """
        SELECT 
            DATE_TRUNC('month', E.timestamp) AS Month,
            D.username AS Driver,
            COUNT(*) AS Count_of_Trips
        FROM rides_rideevent E
        JOIN rides_ride R ON E.ride_id = R.id
        JOIN users_user D ON R.driver_id = D.id
        WHERE E.description = 'Status changed to dropoff'
          AND E.timestamp - (
              SELECT MIN(E2.timestamp)
              FROM rides_rideevent E2
              WHERE E2.ride_id = R.id AND E2.description = 'Status changed to pickup'
          ) > INTERVAL '1 hour'
        GROUP BY Month, Driver;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        # Format the results for JSON response
        formatted_result = [
            {"Month": row[0].strftime('%Y-%m'), "Driver": row[1], "Count_of_Trips": row[2]}
            for row in result
        ]
        return Response(formatted_result)


from django.urls import reverse_lazy
from .models import Ride

class RideListView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/list.html'
    context_object_name = 'rides'
    paginate_by = 10
        

    def get_queryset(self):
        user = self.request.user

        # Définir la base du queryset
        if user.is_admin:  # Si l'utilisateur est admin, il peut voir tous les rides
            queryset = Ride.objects.all()
        elif user.is_rider:  # Si l'utilisateur est un rider, il ne voit que ses rides
            queryset = Ride.objects.filter(rider=user)
        else:  # Pour les autres utilisateurs, aucun ride n'est affiché
            return Ride.objects.none()  # Retourne un queryset vide

        # Filtrage basé sur l'email
        email = self.request.GET.get('email')
        if email:
            queryset = queryset.filter(rider__email__icontains=email)
            print(f"Filtrage par email : {email}, Résultats : {queryset.count()}") 

        # Filtrage basé sur le statut
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Tri basé sur les options
        order_by = self.request.GET.get('order_by')
        if order_by == 'pickup_time':
            queryset = queryset.order_by('start_time')
        elif order_by == 'distance':
            lat = self.request.GET.get('latitude')
            lng = self.request.GET.get('longitude')
            if lat and lng:
                lat = float(lat)
                lng = float(lng)
                queryset = queryset.annotate(
                    distance=Distance(
                        x1=F('pickup_longitude'),
                        y1=F('pickup_latitude'),
                        x2=Value(lng),
                        y2=Value(lat),
                        output_field=FloatField()
                    )
                ).order_by('distance')

        return queryset




class RideDetailView(LoginRequiredMixin, DetailView):
    model = Ride
    template_name = 'rides/details.html'
    context_object_name = 'ride'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['todays_ride_events'] = self.object.events.filter(timestamp__gte=now() - timedelta(days=1))
        return context


class RideCreateView(LoginRequiredMixin, CreateView):
    model = Ride
    form_class = RideCreateForm
    template_name = 'rides/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the current user to the form
        return kwargs

    def form_valid(self, form):
        form.instance.rider = self.request.user  # Set the rider to the logged-in user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ride-list')



class RideUpdateView(LoginRequiredMixin, UpdateView):
    model = Ride
    form_class = RideUpdateForm
    template_name = 'rides/update.html'  # Nom du template pour la mise à jour
    success_url = reverse_lazy('ride-list')  # Redirection après succès

    def get_form_kwargs(self):
        """
        Passe le statut actuel au formulaire pour ajuster les champs dynamiquement.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['instance'] = self.object
        #kwargs['status'] = self.object.status  # Passe le statut actuel
        return kwargs

    def form_valid(self, form):
        logger.debug(f"Form data before save: {form.cleaned_data}")
        ride = form.save(commit=False)  # Préparation avant sauvegarde
        logger.debug(f"Ride instance before save: {ride}")
        previous_status = Ride.objects.get(pk=self.object.pk).status  # Ancien statut

        # Logique en fonction du changement de statut
        if ride.status != previous_status:
            if ride.status == 'in_progress' and previous_status == 'scheduled':
                ride.start_time = now()  # Enregistrer l'heure actuelle comme heure de départ
                ride.driver.is_available = False  # Marquer le chauffeur comme occupé
                ride.driver.save()

            if ride.status == 'completed' and previous_status == 'in_progress':
                ride.end_time = now()  # Enregistrer l'heure actuelle comme heure d'arrivée
                ride.driver.is_available = True  # Rendre le chauffeur disponible
                ride.driver.save()
        for field in form.readonly_fields:
            setattr(ride, field, getattr(self.object, field))

        ride.save()
        logger.debug(f"Ride instance after save: {ride}")

        messages.success(self.request, "Ride updated successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Ajoute des données supplémentaires au template.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Ride Information'
        return context
    
    

