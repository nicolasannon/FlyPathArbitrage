# -*- coding: utf-8 -*-
"""

@author: Nicolas ANNON et Léo SALEMI

Bienvenue sur l'outil FlyPath Arbitrage

FlyPath Arbitrage est un outil complet conçu pour analyser, simuler et optimiser les options de vol en utilisant des méthodologies 
basées sur les données. En intégrant des fonctionnalités avancées telles que le suivi de la disponibilité des sièges, 
la catégorisation des classes tarifaires, l'analyse des tendances de prix et la visualisation des itinéraires, FlyPath Arbitrage 
offre aux utilisateurs une capacité unique d'explorer et d'évaluer quantitativement diverses options de vol.

Principales fonctionnalités :
- Filtrage dynamique et affichage des options de vol selon des critères définis par l'utilisateur.
- Analyse des cartes de sièges pour déterminer le nombre de sièges disponibles sur chaque vol.
- Analyse détaillée des prix, y compris les tendances par jour de la semaine et par classe.
- Outils de visualisation pour cartographier les itinéraires et les routes de vol.
- Intégration flexible avec des sources de données supplémentaires pour une prise de décision améliorée.

Développé pour les professionnels du secteur de l'aviation et du voyage, FlyPath Arbitrage allie expertise aéronautique et analyse 
quantitative, en faisant un atout inestimable pour les planificateurs de vols, les analystes de données et les voyageurs.

Mais avant tout, quelques indications pour les utilisateurs !

Penser à bien installer la librairie de notre API amadeus !pip install amadeus
Ainsi que la libraire geopy pour les routes !pip install folium geopy

Penser à bien importer les autres fichier flight_scanner.py et airlines_codes.py

flight_scanner.py regroupant toutes les classes et fonctions utilisées

airlines_codes.py agissant en dictionnaire comprenant tous les codes IATA, afin d améliorer l expérience utilisateur

Pour des requetes rapides, merci de désactiver la fonction show_seat_availability.

Les prix et données fournises sont à titres indicatifs seulement et ne représentent en rien une information commerciale

Cet outil et les fonctions qui le composent ont étés développés par Nicolas ANNON et Léo SALEMI dans le cadre d un projet académique
visant à étudier le pricing de billet d'avion et l'optimisation de ce dernier.

Pour toute information, merci de contacter = n.annoncontact@gmail.com

"""

# main.py
    
from flight_scanner import FlightScanner


if __name__ == "__main__":
    api_key = 'XXXXXX' #You need to have an amadeus API KEY https://developers.amadeus.com/self-service/apis-docs
    api_secret = 'XXXXXX' #You need to have an amadeus PRIVATE API KEY https://developers.amadeus.com/self-service/apis-docs
    api_openCage = "XXXXXX" #https://opencagedata.com/guides/how-to-create-a-new-api-key
    api_eia = "XXXXXX" #https://www.eia.gov/opendata/
    scanner = FlightScanner(api_key, api_secret, api_openCage, api_eia)
    
    origin = 'CDG'  
    destination = 'ALG'  
    departure_date = '2025-03-26'
    
    flights = scanner.search_flights(origin, destination, departure_date)
    
    #scanner.display_top_10_cheapest_options(flights) #Si on veut une liste des vols les moins chers
    # scanner.display_flight_options(flights) #Si on veut les infos completes
    #scanner.display_flight_options(flights, show_cabin_class=False, show_seat_availability=False) #Si on veut uniquement prix et compagnie
    flights_options = flight_options = scanner.display_flight_options(flights, show_seat_availability=False) #Si on veut afficher sans les options de sieges dispo

    #scanner.display_cabin_classes(flights) #Si on veut les infos cabine avec les sièges filtrés
    
    """
    Si on veut les stats de vols avec graphique
    """
    
    statistics = scanner.calculate_statistics(flights)
    scanner.plot_statistics(statistics)
    
    # scanner.inspect_full_data(flights) # Si on veut toutes les données de l'API    
    
    """
    Autres fonctions d'étude de marché
    """

    filtered_flights = scanner.filter_flights(flights, max_stops=1, airlines=['AF', '5O']) #Filtrer les vols selon des critères spécifiques (Air France, ASL Airlines)
    print("\n--- Filtered Flights (Air France and ASL Airlines) ---")
    scanner.display_flight_options(filtered_flights)
    
    print("\n--- Analyse des prix par jour de la semaine ---")
    price_by_weekday = scanner.analyze_prices_by_weekday(flights) #Analyse des prix par jour de la semaine
    for day, price in price_by_weekday.items():
        print(f"{day}: {price:.2f} EUR en moyenne")
    
    print("\n--- Prix moyen par compagnie aérienne ---")
    average_price_by_airline = scanner.calculate_average_price_by_airline(flights) # Calcul du prix moyen par compagnie aérienne
    for airline, price in average_price_by_airline.items():
        print(f"{airline}: {price:.2f} EUR en moyenne")
    
    print("\n--- Comparaison des cabines ---")
    cabin_comparisons = scanner.compare_cabins(filtered_flights) #Comparaison des cabines pour les vols filtrés
    for i, comparison in enumerate(cabin_comparisons, 1):
        print(f"Option {i}: {comparison}")
    
    print("\n--- Visualisation des itinéraires ---") #Visualisation des itinéraires (affichage des durées des segments)
    scanner.visualize_itineraries(filtered_flights)
    
    # print("\n--- Affichage limité à 10 options ---")
    # test = scanner.display_flight_options(flights, limit=10, show_cabin_class=True, show_seat_availability=True) #Affichage des options de vol avec une limite de résultats (par exemple, 10 résultats)

    # print("\n--- Stockage des options de vol dans une liste ---")
    # flight_options_list = scanner.display_flight_options(flights, limit=5, show_cabin_class=True, show_seat_availability=True)
    # print(flight_options_list)
    
    # flights = scanner.search_flights('CDG', 'ALG', '2024-09-26') #Enregistrer une carte de vol 
    # if flights:
    #     scanner.plot_flight_route(flights[0]) 
    
    
    # jet_fuel_prices = scanner.get_jet_fuel_price(start_date="2024-01-01", end_date="2024-08-16") #Ne marche pas encore totalement
    # print(jet_fuel_prices)
    
    """
    Simulateur de coût de vol
    """
    
    cost_estimate = scanner.estimate_flight_cost(
        aircraft_type="Airbus 737",
        passengers=150,
        bags_per_passenger=1,
        departure_airport="CDG",
        arrival_airport="ALG",
        fuel_price_per_litre= 1.2
    )
    
    print(cost_estimate)
        
        
