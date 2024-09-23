from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import OuterRef, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from .models import City, Country, AirLine, Airport, Package, Tour, Continent
from .serializers import (
    CitySerializer,
    CountrySerializer,
    AirLineSerializer,
    AirportSerializer,
    PackageSerializer,
    TourSerializer,
    ContinentSerializer
)
from .filters import (
    CityFilter,
    CountryFilter,
    AirLineFilter,
    AirportFilter,
    PackageFilter,
    TourFilter,
)
from rest_framework.filters import OrderingFilter

class CityListView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CityFilter

class CountryListView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CountryFilter

class AirLineListView(generics.ListAPIView):
    queryset = AirLine.objects.all()
    serializer_class = AirLineSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AirLineFilter

class AirportListView(generics.ListAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AirportFilter

# class PackageListView(generics.ListAPIView):
#     queryset = Package.objects.all()
#     serializer_class = PackageSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = PackageFilter
    
class PackageListView(generics.ListAPIView):
    serializer_class = PackageSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)

    def get_queryset(self):
        queryset = Package.objects.all().prefetch_related('tours')

        # Get filter parameters from the request
        tour_price_gte = self.request.query_params.get('tour_price__gte')
        tour_price_lte = self.request.query_params.get('tour_price__lte')
        tour_type = self.request.query_params.get('tour_type')  # Example filter for tour type

        # Filter based on tour prices
        if tour_price_gte or tour_price_lte:
            tour_queryset = Tour.objects.filter(package=OuterRef('pk'))
            if tour_price_gte:
                queryset = queryset.annotate(min_price=Subquery(tour_queryset.values('price').filter(price__gte=tour_price_gte).order_by('price')[:1]))
            if tour_price_lte:
                queryset = queryset.annotate(max_price=Subquery(tour_queryset.values('price').filter(price__lte=tour_price_lte).order_by('-price')[:1]))

            if tour_price_gte:
                queryset = queryset.filter(min_price__isnull=False)
            if tour_price_lte:
                queryset = queryset.filter(max_price__isnull=False)

        # Filter based on tour type if provided
        if tour_type:
            queryset = queryset.filter(tours__tour_type=tour_type).distinct()

        return queryset

    filterset_fields = {
        'city': ['exact'],
        'country': ['exact'],
        'created_at': ['gte', 'lte'],
        # Add more filters as needed
    }

    ordering_fields = ['created_at', 'tours__price', 'tours__start_date']  # Allow ordering by tour fields
    ordering = ['created_at']  # Default ordering

class TourListView(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TourFilter
    
    
class NavbarAPIView(APIView):
    def get(self, request):
        # Correctly prefetch related countries and cities
        continents = Continent.objects.prefetch_related('countries__cities').all()
        continent_data = ContinentSerializer(continents, many=True).data
        
        # Construct the nested structure for the navbar
        navbar = []
        for continent in continent_data:
            continent_entry = {
                "id": continent['id'],
                "name": continent['name'],
                "children": []
            }
            for country in continent.get('countries', []):
                country_entry = {
                    "id": country['id'],
                    "name": country['name'],
                    "children": []
                }
                for city in country.get('cities', []):
                    city_entry = {
                        "id": city['id'],
                        "name": city['name'],
                        "path": f"/{country['name']}-tour-{city['name']}"  # Customize path as needed
                    }
                    country_entry["children"].append(city_entry)

                continent_entry["children"].append(country_entry)

            navbar.append(continent_entry)
        about = {
            "id": "184",
            "name": "درباره ما",
            "path": "/about"
        }
        contact = {
            "id": "780",
            "name": "تماس با ما",
            "path": "/contact"
        }
        navbar.append(about)
        navbar.append(contact)
        return Response(navbar)