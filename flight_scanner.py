# -*- coding: utf-8 -*-
"""


@author: Nicolas ANNON et Léo SALEMI
"""

# flight_scanner.py


import requests
import time
import matplotlib.pyplot as plt
import numpy as np
from statistics import median
from airline_codes import airline_codes
from amadeus import Client, ResponseError
from collections import defaultdict
from datetime import datetime
import re
import folium
from geopy.geocoders import Nominatim
import math
from geopy.distance import geodesic
import json


class FlightScanner:
    def __init__(self, api_key, api_secret, geocode_api_key=None, eia_api_key=None):
        """
        Permet l'initalisation de notre client Amadeus API, gérer nos token d'accès, et renseigner les différents code d'API GEOCODE ET EIA.
        
        :param api_key: Your Amadeus API key.
        :param api_secret: Your Amadeus API secret.
        :param geocode_api_key: Your OpenCage Geocode API key for retrieving airport coordinates.
        :param eia_api_key: Your EIA API key for retrieving jet fuel prices.
        """
        self.amadeus = Client(client_id=api_key, client_secret=api_secret)
        self.api_key = api_key
        self.api_secret = api_secret
        self.geocode_api_key = geocode_api_key
        self.eia_api_key = eia_api_key
        self.access_token = None
        self.base_url = "https://test.api.amadeus.com/v1"
        self.get_access_token()
    
    def get_access_token(self):
        """
        Permet d'obtenir un token d'accès pour notre API.
        """
        if not self.access_token:
            url = f"{self.base_url}/security/oauth2/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            body = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret
            }
            response = requests.post(url, headers=headers, data=body)
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
            else:
                print(f"Failed to obtain access token: {response.status_code} - {response.text}")
        return self.access_token
    
    def search_flights(self, origin, destination, departure_date, return_date=None):
        """
        Rechercher des vols entre différentes dates.
        
        :param origin: The IATA code of the departure city (e.g., 'LON' for London).
        :param destination: The IATA code of the arrival city (e.g., 'NYC' for New York).
        :param departure_date: The departure date in 'YYYY-MM-DD' format.
        :param return_date: The return date in 'YYYY-MM-DD' format, if it's a round trip.
        :return: A list of flight offers.
        """
        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=1
            )
            return response.data
        except ResponseError as error:
            print(f"An error occurred during flight search: {error}")
            return []
        
        except ResponseError as error:
            print(f"An error occurred: {error}")
            return []

    def display_flight_options(self, flights, show_cabin_class=True, show_seat_availability=True, show_price=True, show_airline=True, limit="ALL"):
        """
        Permet l'affichage des options de vols avec des paramètres en arguments tels que si le siège est dispo
        la classe de la cabine et  etc.
        Permet également de stocker les options dans une liste.
    
        :param flights: A list of flight offers returned by the search.
        :param show_cabin_class: Boolean to display cabin class information.
        :param show_seat_availability: Boolean to display seat availability information.
        :param show_price: Boolean to display price information.
        :param show_airline: Boolean to display airline information.
        :param limit: An integer to limit the number of flight options displayed, or "ALL" to show all options.
        :return: A list of dictionaries containing the displayed flight options.
        """
        if not flights:
            print("No flight options found.")
            return []
    
        
        if limit != "ALL":
            limit = min(int(limit), len(flights))
        else:
            limit = len(flights)
    
        flight_options = []  
    
        for idx, flight in enumerate(flights[:limit]):
            option_info = {}
            
    
            seat_info = ""
            if show_seat_availability:
                seat_map = self.get_seat_map(flight)
                if seat_map:
                    available_seats, total_seats = self.count_seats(seat_map)
                    seat_info = f"{available_seats}/{total_seats} seats available"
                else:
                    seat_info = "Seat map data not available"
                option_info['seat_info'] = seat_info
            
            
            if show_seat_availability:
                print(f"Option {idx + 1}: {seat_info}")
                option_info['option'] = f"Option {idx + 1}: {seat_info}"
            else:
                print(f"Option {idx + 1}:")
                option_info['option'] = f"Option {idx + 1}:"
    
            
            if show_airline:
                airline = flight['validatingAirlineCodes'][0]
                print(f"  Airline: {airline}")
                option_info['airline'] = airline
            
            
            if show_price:
                price = f"{flight['price']['grandTotal']} {flight['price']['currency']}"
                print(f"  Price: {price}")
                option_info['price'] = price
            
            
            segments_info = []
            for itinerary in flight['itineraries']:
                for segment in itinerary['segments']:
                    segment_details = {}
                    departure = segment['departure']['iataCode']
                    arrival = segment['arrival']['iataCode']
                    departure_time = segment['departure']['at']
                    arrival_time = segment['arrival']['at']
                    carrier = segment['carrierCode']
                    aircraft = segment['aircraft']['code']
                    num_seats = flight['numberOfBookableSeats']
                    
                    print(f"  Segment: {departure} ({departure_time}) -> {arrival} ({arrival_time})")
                    print(f"    Operating Airline: {carrier} ({carrier})")
                    print(f"    Aircraft: {aircraft}")
                    print(f"    Number of Bookable Seats: {num_seats}")
                    
                    segment_details['departure'] = departure
                    segment_details['arrival'] = arrival
                    segment_details['departure_time'] = departure_time
                    segment_details['arrival_time'] = arrival_time
                    segment_details['operating_airline'] = carrier
                    segment_details['aircraft'] = aircraft
                    segment_details['number_of_bookable_seats'] = num_seats
                    
                    
                    if show_cabin_class:
                        segment_id = segment['id']
                        fare_details = {fare['segmentId']: fare['cabin'] for traveler in flight['travelerPricings'] for fare in traveler['fareDetailsBySegment']}
                        cabin_class = fare_details.get(segment_id, 'Unknown')
                        print(f"    Cabin Class: {cabin_class}")
                        segment_details['cabin_class'] = cabin_class
    
                    segments_info.append(segment_details)
            option_info['segments'] = segments_info
    
            print("----------------------------------------")
            flight_options.append(option_info)
    
        return flight_options


    def calculate_statistics(self, flights):
        """
        Permet de calculer des statistiques telles que la moyenne, la médiane pour le prix des vols.
        
        :param flights: A list of flight offers.
        :return: A dictionary with airlines as keys and their corresponding statistics.
        """
        airline_prices = {}
        
        for flight in flights:
            airline_code = flight['validatingAirlineCodes'][0]
            price = float(flight['price']['total'])
            
            if airline_code in airline_prices:
                airline_prices[airline_code].append(price)
            else:
                airline_prices[airline_code] = [price]
        
        statistics = {}
        for airline_code, prices in airline_prices.items():
            stats = {
                'mean': np.mean(prices),
                'median': median(prices)
            }
            statistics[airline_code] = stats
        
        return statistics

    def plot_statistics(self, statistics):
        """
        Permet de dessiner les graphiques reprenant les statistiques calculés sur les offres de billets
        
        :param statistics: A dictionary with airlines as keys and their corresponding statistics.
        """
        airlines = []
        means = []
        medians = []
        
        for airline_code, stats in statistics.items():
            airline_name = airline_codes.get(airline_code, airline_code)
            airlines.append(airline_name)
            means.append(stats['mean'])
            medians.append(stats['median'])
        
        x = np.arange(len(airlines))  
        width = 0.35  

        fig, ax = plt.subplots()
        bars_mean = ax.bar(x - width/2, means, width, label='Mean Price')
        bars_median = ax.bar(x + width/2, medians, width, label='Median Price')

        
        ax.set_xlabel('Airline')
        ax.set_ylabel('Price (EUR)')
        ax.set_title('Mean and Median Flight Prices by Airline')
        ax.set_xticks(x)
        ax.set_xticklabels(airlines)
        ax.legend()

        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        
    def display_cabin_classes(self, flights):
        """
        Cette fonction nous permet d'afficher des informations propre à la classe de cabine [ECONOMY, BUSINESS, PREMIUM] ou autre
        
        :param flights: A list of flight offers returned by the search.
        """
        if not flights:
            print("No flight options found.")
            return
        
        for i, flight in enumerate(flights, 1):
            airline = flight['validatingAirlineCodes'][0]
            itinerary = flight['itineraries'][0]['segments']
            fare_details = {fare['segmentId']: fare['cabin'] for traveler in flight['travelerPricings'] for fare in traveler['fareDetailsBySegment']}
            
            print(f"Option {i}:")
            print(f"  Airline: {airline}")
            for segment in itinerary:
                departure = segment['departure']['iataCode']
                arrival = segment['arrival']['iataCode']
                departure_time = segment['departure']['at']
                arrival_time = segment['arrival']['at']
                segment_id = segment['id']
                cabin_class = fare_details.get(segment_id, 'Unknown')
                
                print(f"  Segment: {departure} ({departure_time}) -> {arrival} ({arrival_time})")
                print(f"    Cabin Class: {cabin_class}")
            print("-" * 40)

    def inspect_full_data(self, flights):
        """
        Cette fonction nous permet de checker tous les infos renvoyés par notre API afin de sélectionner ce dont nous avons besoin
        
        :param flights: A list of flight offers returned by the search.
        """
        if not flights:
            print("No flight options found.")
            return
        
        for i, flight in enumerate(flights, 1):
            print(f"Option {i}:")
            print(f"Full flight data: {flight}")
            print("-" * 40)
    def display_top_10_cheapest_options(self, flights):
        """
        Cette fonctionnalité nous permet d'afficher les 10 options les moins chères
        
        :param flights: A list of flight offers returned by the search.
        """
        if not flights:
            print("No flight options found.")
            return
        
        
        sorted_flights = sorted(flights, key=lambda x: float(x['price']['total']))
        
        
        top_10_flights = sorted_flights[:10]
        
        for i, flight in enumerate(top_10_flights, 1):
            price = flight['price']['total']
            airline = flight['validatingAirlineCodes'][0]
            itinerary = flight['itineraries'][0]['segments']
            
            print(f"Option {i}:")
            print(f"  Airline: {airline}")
            print(f"  Price: {price} EUR")
            for segment in itinerary:
                departure = segment['departure']['iataCode']
                arrival = segment['arrival']['iataCode']
                departure_time = segment['departure']['at']
                arrival_time = segment['arrival']['at']
                print(f"  Segment: {departure} ({departure_time}) -> {arrival} ({arrival_time})")
            print("-" * 40)


    def get_seat_map(self, flight_offer):
        url = f"{self.base_url}/shopping/seatmaps"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/vnd.amadeus+json",
        }
        body = {"data": [flight_offer]}
        
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            seatmap_data = response.json()
            return seatmap_data
        else:
            print(f"Error retrieving seat map: {response.status_code} - {response.text}")
            return None
    
            
    def check_seat_availability(self, flights):
        for idx, flight in enumerate(flights):
            print(f"Option {idx + 1}:")
            print(f"  Airline: {flight['validatingAirlineCodes'][0]}")
            print(f"  Price: {flight['price']['grandTotal']} {flight['price']['currency']}")
            
            
            for itinerary in flight['itineraries']:
                for segment in itinerary['segments']:
                    print(f"  Segment: {segment['departure']['iataCode']} -> {segment['arrival']['iataCode']}")
                    print(f"    Departure: {segment['departure']['at']}")
                    print(f"    Arrival: {segment['arrival']['at']}")
                    print(f"    Aircraft: {segment['aircraft']['code']}")
                    print(f"    Number of Bookable Seats: {flight['numberOfBookableSeats']}")
    
                    seat_map = self.get_seat_map(flight)
                    if seat_map:
                        available_seats, total_seats = self.count_seats(seat_map)
                        print(f"    Seat Availability: {available_seats}/{total_seats} seats available")
                    else:
                        print("    Seat map data not available")
            print("----------------------------------------")          
            
    def aggregate_seat_data(self, flights):
        for idx, flight in enumerate(flights):
            seatmap_data = self.get_seat_map(flight)
            if seatmap_data:
                available_seats, total_seats = self.count_seats(seatmap_data)
                print(f"Option {idx + 1}: {available_seats}/{total_seats} seats available")
            else:
                print(f"Option {idx + 1}: Seat map data not available")
                
    def count_available_seats(self, seatmap_data):
        available_seats = 0
        
        
        if seatmap_data and isinstance(seatmap_data, dict) and 'data' in seatmap_data:
            seatmap = seatmap_data['data'][0]  
            for deck in seatmap.get('decks', []):
                for seat in deck.get('seats', []):
                    for pricing in seat.get('travelerPricing', []):
                        if pricing.get('seatAvailabilityStatus') == 'AVAILABLE':
                            available_seats += 1
        else:
            print("Unexpected seat map data structure or empty data.")
        
        return available_seats
    
    def count_seats(self, seatmap_data):
        available_seats = 0
        total_seats = 0
    
        if seatmap_data and isinstance(seatmap_data, dict) and 'data' in seatmap_data:
            seatmap = seatmap_data['data'][0]  
            for deck in seatmap.get('decks', []):
                for seat in deck.get('seats', []):
                    total_seats += 1
                    for pricing in seat.get('travelerPricing', []):
                        if pricing.get('seatAvailabilityStatus') == 'AVAILABLE':
                            available_seats += 1
        else:
            print("Unexpected seat map data structure or empty data.")
    
        return available_seats, total_seats

    """
    
    Cette partie utilise une autre partie encore de l'API afin de permettre une analyse commerciale plus en profondeur
    
    """
    
    def _get_weekday(self, date_str):
        """
        Retourne le jour de la semaine pour une date donnée.
        
        :param date_str: La date au format ISO (YYYY-MM-DDTHH:MM:SS).
        :return: Le jour de la semaine en texte (ex. "Monday").
        """
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime('%A')


    def filter_flights(self, flights, max_duration=None, max_stops=None, airlines=None, cabin_class=None):
            filtered_flights = []
            for flight in flights:
                add_flight = True
                for itinerary in flight['itineraries']:
                    if max_duration and self._get_duration(itinerary['duration']) > max_duration:
                        add_flight = False
                    if max_stops and any(segment['numberOfStops'] > max_stops for segment in itinerary['segments']):
                        add_flight = False
                    if airlines and flight['validatingAirlineCodes'][0] not in airlines:
                        add_flight = False
                    if cabin_class:
                        for traveler in flight['travelerPricings']:
                            if all(detail['cabin'] != cabin_class for detail in traveler['fareDetailsBySegment']):
                                add_flight = False
                if add_flight:
                    filtered_flights.append(flight)
            return filtered_flights
        
    def analyze_prices_by_weekday(self, flights):
        """
        Analyse des prix moyens par jour de la semaine.

        :param flights: La liste des offres de vol.
        :return: Un dictionnaire des prix moyens par jour de la semaine.
        """
        prices_by_day = {}
        count_by_day = {}

        for flight in flights:
            for itinerary in flight['itineraries']:
                for segment in itinerary['segments']:
                    departure_day = self._get_weekday(segment['departure']['at'])
                    price = float(flight['price']['grandTotal'])

                    if departure_day not in prices_by_day:
                        prices_by_day[departure_day] = 0.0
                        count_by_day[departure_day] = 0

                    prices_by_day[departure_day] += price
                    count_by_day[departure_day] += 1

        
        for day in prices_by_day:
            prices_by_day[day] /= count_by_day[day]

        return prices_by_day
    
    def calculate_average_price_by_airline(self, flights):
        price_by_airline = defaultdict(list)
        for flight in flights:
            airline = flight['validatingAirlineCodes'][0]
            price_by_airline[airline].append(float(flight['price']['grandTotal']))
        average_price_by_airline = {airline: sum(prices)/len(prices) for airline, prices in price_by_airline.items()}
        return average_price_by_airline
    
    def compare_cabins(self, flights):
        comparison_results = []
        for flight in flights:
            cabin_comparison = {}
            for traveler in flight['travelerPricings']:
                for segment in traveler['fareDetailsBySegment']:
                    cabin = segment['cabin']
                    price = float(traveler['price']['total'])
                    if cabin not in cabin_comparison or price < cabin_comparison[cabin]:
                        cabin_comparison[cabin] = price
            comparison_results.append(cabin_comparison)
        return comparison_results
    
    def visualize_itineraries(self, flights):
        """
        Visualise les itinéraires de vol en utilisant une représentation simple.

        :param flights: La liste des offres de vol filtrées.
        """
        import matplotlib.pyplot as plt

        for idx, flight in enumerate(flights):
            times = []
            labels = []
            for itinerary in flight['itineraries']:
                for segment in itinerary['segments']:
                    times.append(self._get_duration(segment['duration']))
                    labels.append(f"{segment['departure']['iataCode']} -> {segment['arrival']['iataCode']}")
            
            plt.figure(figsize=(10, 6))
            plt.barh(labels, times, color='skyblue')
            plt.xlabel('Duration (minutes)')
            plt.ylabel('Flight Segment')
            plt.title(f'Itinerary {idx + 1}')
            plt.show()
            
    def _get_duration(self, duration_str):
        """
        Convertit une durée au format ISO 8601 en nombre de minutes.

        :param duration_str: La durée au format ISO 8601 (ex. "PT2H30M").
        :return: La durée en minutes.
        """
        match = re.match(r'PT(\d+H)?(\d+M)?', duration_str)
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        return hours * 60 + minutes
    
    def plot_flight_route(self, flight):
        """Génère une carte affichant la route du vol entre l'aéroport de départ et l'aéroport d'arrivée."""
        segments = flight['itineraries'][0]['segments']
        departure_airport = segments[0]['departure']['iataCode']
        arrival_airport = segments[-1]['arrival']['iataCode']
        
        departure_coords = self.get_airport_coordinates(departure_airport)
        arrival_coords = self.get_airport_coordinates(arrival_airport)
        
        if departure_coords and arrival_coords:
            
            map_center = [(departure_coords[0] + arrival_coords[0]) / 2, (departure_coords[1] + arrival_coords[1]) / 2]
            flight_map = folium.Map(location=map_center, zoom_start=4)
            
            
            folium.Marker(location=departure_coords, popup=f"Départ: {departure_airport}").add_to(flight_map)
            folium.Marker(location=arrival_coords, popup=f"Arrivée: {arrival_airport}").add_to(flight_map)
            
            
            folium.PolyLine(locations=[departure_coords, arrival_coords], color="blue", weight=2.5).add_to(flight_map)
            
            
            flight_map.save("flight_route.html")
            print("La carte de la route du vol a été générée: flight_route.html")
        else:
            print("Les coordonnées des aéroports n'ont pas pu être trouvées.")

    """
    
    Cette partie permet un calculateur de coût de vol approximatif 
    
    """
    
    
    def calculate_distance(self, departure_airport, arrival_airport):
        departure_coords = self.get_airport_coordinates(departure_airport)
        arrival_coords = self.get_airport_coordinates(arrival_airport)

        if departure_coords and arrival_coords:
            return geodesic(departure_coords, arrival_coords).km
        else:
            print("Impossible de calculer la distance, coordonnées manquantes.")
            return None
    
    def estimate_flight_cost(self, aircraft_type, passengers, bags_per_passenger, departure_airport, arrival_airport, fuel_price_per_litre):
        
        fuel_consumption_per_hour = 2500  # litres par heure moyenne pour Boeing 737
        average_speed_kmh = 850  # vitesse moyenne en km/h
        crew_cost_per_hour = 500  # EUR
        airport_fees = 2000  # EUR, approximation
        maintenance_cost_per_hour = 800  # EUR, approximation
        oew = 41413  # poids à vide estimé, d'après la brochure d'un Boeing 737
        mtow = 70534  # Maximum poids embarqué pour un Boeing 737
        
        
        distance_km = self.calculate_distance(departure_airport, arrival_airport)
        
        
        flight_duration_hours = distance_km / average_speed_kmh
        
        
        passenger_weight = 100  # estimation avec un passager + bagage
        total_weight = oew + (passengers * passenger_weight)
        
        
        weight_factor = total_weight / oew
        adjusted_fuel_consumption_per_hour = fuel_consumption_per_hour * (1 + 0.005 * (weight_factor - 1))  # 0.5% D'augmentation par 1% d'augmentation de poids
        total_fuel_needed = adjusted_fuel_consumption_per_hour * flight_duration_hours
        fuel_cost = total_fuel_needed * fuel_price_per_litre
        
        
        crew_cost = crew_cost_per_hour * flight_duration_hours
        maintenance_cost = maintenance_cost_per_hour * flight_duration_hours
        
        
        total_cost = fuel_cost + crew_cost + airport_fees + maintenance_cost
        cost_per_passenger = total_cost / passengers
        
        
        return {
            "Total Cost (EUR)": total_cost,
            "Cost per Passenger (EUR)": cost_per_passenger,
            "Flight Duration (hours)": flight_duration_hours,
            "Fuel Needed (litres)": total_fuel_needed
      }
    def get_airport_coordinates(self, iata_code): 
        url = f"https://api.opencagedata.com/geocode/v1/json?q={iata_code}&key={self.geocode_api_key}&limit=1"
        response = requests.get(url)
        data = response.json()

        if data['results']:
            latitude = data['results'][0]['geometry']['lat']
            longitude = data['results'][0]['geometry']['lng']
            return latitude, longitude
        else:
            print(f"Coordonnées non trouvées pour l'aéroport avec le code IATA {iata_code}.")
            return None

    def get_jet_fuel_price(self, start_date="2024-01-01", end_date="2024-08-16"):
        """
        Pour récupérer les prix du fuel, mais ne fonctionne pas trop encore pour le moment.

        :param start_date: The start date for the data range (format: YYYY-MM-DD).
        :param end_date: The end date for the data range (format: YYYY-MM-DD).
        :return: A dictionary with the date and corresponding fuel price or None if an error occurs.
        """
        api_url = (
            f"https://api.eia.gov/v2/petroleum/pri/spt/data/"
            f"?frequency=weekly&data[0]=value&start={start_date}&end={end_date}"
            f"&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
        )

        
        response = requests.get(api_url, headers={"api_key": self.eia_api_key})

        
        if response.status_code == 200:
            
            data = response.json()

           
            try:
                fuel_prices = [
                    {"date": entry['period'], "price_per_gallon": entry['value']}
                    for entry in data['response']['data']
                ]
                return fuel_prices
            except KeyError as e:
                print(f"Key error: {e}")
                return None
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return None