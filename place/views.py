from django.db.models import Q
from django.views.generic import View
from django.http import JsonResponse

from place.models import City
from place.models import State
from place.models import Country


def country_as_JSON(country):
    return {
        'name': country.name,
        'code': country.code,
        'flag': country.flag,
    }


class CountrySearch(View):
    def get(self, request, *args, **kwargs):
        country_list = []

        if 'q' in request.GET and request.GET.get('q'):
            query = request.GET.get('q')
            query_set = Country.objects.filter(
                Q(name__icontains=query)
            ).distinct()

            for country in query_set:
                country_list.append(country_as_JSON(country.country))

        return JsonResponse(country_list, safe=False)


def city_as_JSON(city):
    name = '{0} - {1} - {2}'.format(
        city.name,
        city.state,
        city.country.country.name,
    )

    return {
        'id': city.id,
        'name': name,
    }


class CitySearch(View):
    def get(self, request, *args, **kwargs):
        city_list = []

        if 'q' in request.GET and request.GET.get('q'):
            query = request.GET.get('q')
            query_set = City.objects.filter(
                Q(name__icontains=query) |
                Q(state__name__icontains=query),
            ).distinct()

            for city in query_set:
                city_list.append(city_as_JSON(city))

        return JsonResponse(city_list, safe=False)


class CityCreate(View):
    def post(self, request, **kwargs):
        city_name = request.POST.get('city_name')
        state_long_name = request.POST.get('state_long_name')
        country_short_name = request.POST.get('country_short_name')

        country_instance = None
        state_object = None
        city_object = None
        city_dict = {}

        if country_short_name:
            country_instance = Country.objects.get_or_create(
                country=country_short_name,
            )[0]

        if state_long_name and country_instance:
            state_object = State.objects.get_or_create(
                name=state_long_name,
                country=country_instance,
            )[0]

        if city_name and country_instance:
            city_object = City.objects.get_or_create(
                name=city_name,
                state=state_object,
                country=country_instance,
            )[0]

        if city_object:
            city_dict = {
                'city_name': city_object.name,
                'city_id': city_object.id,
                'country_name': country_instance.country.name,
                'country_code': country_instance.country.code,
                'country_gif': '/static/flags/{}.gif'.format(
                    country_instance.country.code.lower(),
                ),
            }

        return JsonResponse(
            {
                'status': 'success',
                'city_dict': city_dict,
            }
        )