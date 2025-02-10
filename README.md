# FlyPathArbitrage

Fly Path, an optimization model designed to enhance flight scheduling and improve operating margins.

  Simulation & Cost Analysis: Created a tool to simulate flight costs, compare pricing strategies, and evaluate market opportunities.
  Operational Constraints Integration: Incorporated key airline constraints, including revenue matrices, cost structures, crew schedules, and fleet availability, to generate realistic scheduling solutions.
  Market Strategy & Pricing Optimization: Analyzed key routes, balancing dynamic fares and niche market positioning to maximize profitability.
  Case Study – ASL Airlines France: Assessed the impact of flexible pricing strategies, identifying routes with aggressive fare competition (e.g., CDG-ALG) versus premium pricing on high-demand routes.

1. Overview of the Files

    airline_codes.py: A dictionary mapping airline IATA codes to their full company names.
    flight_scanner.py: The main module containing the FlightScanner class, which handles flight search, price analysis, and data visualization.
    main.py: The primary script that initializes a FlightScanner object, runs API queries, and displays the results.

2. How These Files Work Together

    Loading Airline Data
        flight_scanner.py imports airline_codes.py to convert IATA codes into readable airline names.

    Initializing the Flight Search API
        main.py creates a FlightScanner object using API keys.

    Searching and Displaying Flights
        search_flights() queries the Amadeus API and retrieves available flight offers.
        display_flight_options() formats and presents the results.

    Analyzing and Generating Statistics
        calculate_statistics() extracts key metrics (average and median prices).
        plot_statistics() visualizes price trends per airline.
        analyze_prices_by_weekday() identifies the cheapest days to fly.

    Visualizing Flight Routes
        visualize_itineraries() presents flight routes using graphs.
        plot_flight_route() generates an interactive map of flight paths.

    Simulating Flight Costs
        estimate_flight_cost() calculates an estimated operational cost for a flight, considering:
            Fuel consumption
            Flight duration
            Airport and crew fees
            Passenger load

3. Main Functions and Their Roles
flight_scanner.py (Class FlightScanner)

    search_flights(origin, destination, departure_date)
    Retrieves available flights between two airports.
    display_flight_options(flights, show_cabin_class=True, show_seat_availability=True)
    Displays flight details, including airline, price, and seat availability.
    calculate_statistics(flights)
    Computes statistical insights on flight prices, including averages and medians.
    plot_statistics(statistics)
    Generates a graph comparing price distributions across airlines.
    analyze_prices_by_weekday(flights)
    Determines the average price for each day of the week.
    visualize_itineraries(flights)
    Creates graphical representations of flight durations.
    estimate_flight_cost(aircraft_type, passengers, departure_airport, arrival_airport, fuel_price_per_litre)
    Estimates the total cost and cost per passenger for a flight.

main.py

   Initializes the FlightScanner object with API credentials.
   Executes flight searches using search_flights().
   Displays statistics and visualizations with plot_statistics() and visualize_itineraries().
   Simulates flight cost estimates using estimate_flight_cost().
