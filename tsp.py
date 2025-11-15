#!/usr/bin/env python

"""
This is a command-line tool that figures out the shortest distance to visit all cities in a list.
Enhanced with:
- Statistical analysis of convergence
- Progress tracking
- Cached geocoding for performance
- Automatic optimal simulation detection
- Results export
"""


import geopy
import geopy.distance
import pandas as pd
from random import shuffle
import click
import time
import json
from pathlib import Path

# build a function that takes variable length argument of strings and returns a list of cities
def my_cities(*args):
    """Build a list of cities from input"""
    return list(args)


def load_cached_coordinates():
    """Load cached city coordinates from file"""
    cache_file = Path("city_coordinates_cache.json")
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return json.load(f)
    return {}


def save_cached_coordinates(cache):
    """Save city coordinates to cache file"""
    cache_file = Path("city_coordinates_cache.json")
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)


def create_cities_dataframe(cities=None, use_cache=True):
    """Create a Pandas DataFrame of cities and their latitudes and longitudes
    
    Args:
        cities: List of city names (optional)
        use_cache: Whether to use cached coordinates for faster loading
    """

    cache = load_cached_coordinates() if use_cache else {}
    
    if cities is None:
        cities = [
            "New York",
            "Knoxville",
            "Birmingham",
            "Baltimore",
            "Bangor",
            "Cleveland",
            "Chicago",
            "Denver",
            "Los Angeles",
            "San Francisco",
            "Raleigh",
            "Seattle",
            "Boston",
            "Houston",
            "Dallas",
            "Miami",
            "Atlanta",
            "Fort Worth",
            "Phoenix",
            "San Diego",
        ]

    # create a list to hold the latitudes and longitudes
    latitudes = []
    longitudes = []
    geolocator = geopy.geocoders.Nominatim(user_agent="tsp_pandas")
    
    # loop through the cities list and get the latitudes and longitudes
    for city in cities:
        if city in cache:
            # Use cached coordinates
            latitudes.append(cache[city]['latitude'])
            longitudes.append(cache[city]['longitude'])
        else:
            # Fetch from API and cache
            location = geolocator.geocode(city)
            if location:
                latitudes.append(location.latitude)
                longitudes.append(location.longitude)
                cache[city] = {
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }
            time.sleep(1)  # Respect API rate limits
    
    # Save updated cache
    if use_cache and cache:
        save_cached_coordinates(cache)
    # create a dataframe from the cities, latitudes, and longitudes
    df = pd.DataFrame(
        {
            "city": cities,
            "latitude": latitudes,
            "longitude": longitudes,
        }
    )
    return df


def tsp(cities_df, verbose=False):
    """Traveling Salesman Problem using Pandas and Geopy
    
    Args:
        cities_df: DataFrame with city information
        verbose: Whether to print detailed output
    """

    # create a list of cities
    city_list = cities_df["city"].to_list()
    # shuffle the list to randomize the order of the cities
    shuffle(city_list)
    if verbose:
        print(f"Randomized city_list: {city_list}")
    # create a list of distances
    distance_list = []
    # loop through the list
    for i in range(len(city_list)):
        # if i is not the last item in the list
        if i != len(city_list) - 1:
            # get the distance between the current city and the next city
            distance = geopy.distance.distance(
                (
                    cities_df[cities_df["city"] == city_list[i]]["latitude"].values[0],
                    cities_df[cities_df["city"] == city_list[i]]["longitude"].values[0],
                ),
                (
                    cities_df[cities_df["city"] == city_list[i + 1]]["latitude"].values[
                        0
                    ],
                    cities_df[cities_df["city"] == city_list[i + 1]][
                        "longitude"
                    ].values[0],
                ),
            ).miles
            # append the distance to the distance list
            distance_list.append(distance)
        # if i is the last item in the list
        else:
            # get the distance between the current city and the first city
            distance = geopy.distance.distance(
                (
                    cities_df[cities_df["city"] == city_list[i]]["latitude"].values[0],
                    cities_df[cities_df["city"] == city_list[i]]["longitude"].values[0],
                ),
                (
                    cities_df[cities_df["city"] == city_list[0]]["latitude"].values[0],
                    cities_df[cities_df["city"] == city_list[0]]["longitude"].values[0],
                ),
            ).miles
            # append the distance to the distance list
            distance_list.append(distance)
    # return the sum of the distance list and the city list
    total_distance = sum(distance_list)
    return total_distance, city_list


def analyze_convergence(distance_list, window=5):
    """Analyze if the algorithm has converged
    
    Returns improvement rate over the last window of simulations
    """
    if len(distance_list) < window:
        return None
    
    recent_best = min(distance_list[-window:])
    previous_best = min(distance_list[:-window])
    
    improvement = (previous_best - recent_best) / previous_best * 100
    return improvement


def main(count, df=None, verbose=True, auto_stop=False, improvement_threshold=0.1):
    """Main function that runs the tsp simulation multiple times
    
    Args:
        count: Maximum number of simulations to run
        df: Pre-loaded cities DataFrame (optional)
        verbose: Print detailed progress
        auto_stop: Stop early if convergence is detected
        improvement_threshold: Threshold for convergence detection (percentage)
    """
    start_time = time.time()
    
    # create a list to hold the distances
    distance_list = []
    # create a list to hold the city lists
    city_list_list = []
    
    # loop through the simulation
    if df is None:
        print("Loading cities data...")
        cdf = create_cities_dataframe(use_cache=True)
    else:
        cdf = df
    
    print(f"\nStarting TSP optimization with up to {count} simulations...\n")
    
    best_distance = float('inf')
    iterations_since_improvement = 0
    
    for i in range(count):  # run the simulation x times
        # get the distance and city list
        distance, city_list = tsp(cdf, verbose=False)
        
        # append the distance to the distance list
        distance_list.append(distance)
        # append the city list to the city list list
        city_list_list.append(city_list)
        
        # Track improvements
        if distance < best_distance:
            best_distance = distance
            iterations_since_improvement = 0
            improvement_marker = " ⭐ NEW BEST!"
        else:
            iterations_since_improvement += 1
            improvement_marker = ""
        
        if verbose:
            print(f"Simulation {i+1:3d}/{count}: Distance = {distance:8.2f} miles{improvement_marker}")
        
        # Check for convergence
        if auto_stop and i >= 10:
            improvement = analyze_convergence(distance_list, window=5)
            if improvement is not None and abs(improvement) < improvement_threshold:
                print(f"\n🎯 Convergence detected after {i+1} simulations (improvement < {improvement_threshold}%)")
                break
            
            if iterations_since_improvement >= 20:
                print(f"\n🎯 No improvement in last 20 iterations. Stopping at {i+1} simulations.")
                break
    
    elapsed_time = time.time() - start_time
    
    # get the index of the shortest distance
    shortest_distance_index = distance_list.index(min(distance_list))
    
    # Print statistics
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Total Simulations Run: {len(distance_list)}")
    print(f"Execution Time: {elapsed_time:.2f} seconds")
    print(f"\nShortest Distance: {min(distance_list):.2f} miles")
    print(f"Average Distance: {sum(distance_list)/len(distance_list):.2f} miles")
    print(f"Longest Distance: {max(distance_list):.2f} miles")
    print(f"Standard Deviation: {pd.Series(distance_list).std():.2f} miles")
    print(f"\nImprovement: {(max(distance_list) - min(distance_list)):.2f} miles ({(max(distance_list) - min(distance_list))/max(distance_list)*100:.1f}%)")
    print(f"\nOptimal Route Found:")
    print(" -> ".join(city_list_list[shortest_distance_index]))
    print("="*60)
    
    # Save results
    results = {
        "simulations": len(distance_list),
        "execution_time": elapsed_time,
        "best_distance": min(distance_list),
        "average_distance": sum(distance_list)/len(distance_list),
        "worst_distance": max(distance_list),
        "best_route": city_list_list[shortest_distance_index],
        "all_distances": distance_list
    }
    
    with open("tsp_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n💾 Results saved to tsp_results.json")
    
    return results


# create click group
@click.group()
def cli():
    """This is a command-line tool that figures out the shortest distance to visit all cities in a list."""


# create a click command that takes a variable number of arguments of cities passed in
@cli.command("cities")
@click.argument("cities", nargs=-1)
@click.option("--count", default=5, help="Number of simulations to run")
def cities_cli(cities, count):
    """This is a command-line tool that figures out the shortest distance to visit all cities in a list.

    Example: ./fetch_cities_lat_long.py cities "New York" "Knoxville" --count 2
    """

    # create a list of cities
    city_list = my_cities(*cities)
    # create a dataframe of cities and their latitudes and longitudes
    cities_df = create_cities_dataframe(city_list)
    # run the tsp function
    main(count, cities_df)


# add click command that runs the similation x times
@cli.command("simulate")
@click.option("--count", default=10, help="Number of times to run the simulation.")
@click.option("--auto-stop", is_flag=True, help="Automatically stop when convergence is detected")
@click.option("--quiet", is_flag=True, help="Suppress detailed iteration output")
@click.option("--threshold", default=0.1, help="Improvement threshold for convergence (%)")
def simulate(count, auto_stop, quiet, threshold):
    """Run the simulation x times and print the shortest distance and cities visited.

    Examples:
        python tsp.py simulate --count 50
        python tsp.py simulate --count 100 --auto-stop
        python tsp.py simulate --count 200 --auto-stop --quiet

    """

    main(count, verbose=not quiet, auto_stop=auto_stop, improvement_threshold=threshold)


@cli.command("benchmark")
@click.option("--max-count", default=100, help="Maximum simulations to test")
def benchmark(max_count):
    """Run benchmark to determine optimal number of simulations
    
    Example:
        python tsp.py benchmark --max-count 100
    """
    print("🔬 Running benchmark to find optimal simulation count...\n")
    
    cdf = create_cities_dataframe(use_cache=True)
    
    test_counts = [5, 10, 20, 30, 50, 75, 100]
    test_counts = [c for c in test_counts if c <= max_count]
    
    results = []
    
    for test_count in test_counts:
        print(f"\nTesting with {test_count} simulations...")
        result = main(test_count, df=cdf, verbose=False, auto_stop=False)
        results.append({
            'count': test_count,
            'best': result['best_distance'],
            'time': result['execution_time']
        })
    
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    print(f"{'Simulations':<15} {'Best Distance':<20} {'Time (s)':<15} {'Efficiency'}")
    print("-"*60)
    
    best_overall = min(r['best'] for r in results)
    
    for r in results:
        efficiency = (best_overall / r['best']) / (r['time'] / results[0]['time'])
        marker = " ⭐" if r['best'] == best_overall else ""
        print(f"{r['count']:<15} {r['best']:<20.2f} {r['time']:<15.2f} {efficiency:.2f}{marker}")
    
    print("="*60)
    print("\n📊 Recommendation:")
    print(f"   - For quick results: 10-20 simulations")
    print(f"   - For balanced performance: 30-50 simulations")
    print(f"   - For best accuracy: 75-100+ simulations")
    print(f"   - Use --auto-stop flag for automatic convergence detection")
    print("\n💡 Tip: Run 'python tsp.py simulate --count 50 --auto-stop' for optimal balance")


if __name__ == "__main__":
    cli()


# run the main function
if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()