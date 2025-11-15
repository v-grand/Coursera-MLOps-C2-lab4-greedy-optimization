"""
Tests for TSP optimization enhancements
"""

import pytest
import pandas as pd
from tsp import (
    create_cities_dataframe,
    tsp,
    analyze_convergence,
    load_cached_coordinates,
    save_cached_coordinates,
)
import json
from pathlib import Path


def test_create_cities_dataframe_with_cache():
    """Test that cities dataframe can be created with caching"""
    cities = ["New York", "Boston"]
    df = create_cities_dataframe(cities, use_cache=True)
    
    assert len(df) == 2
    assert "city" in df.columns
    assert "latitude" in df.columns
    assert "longitude" in df.columns
    assert df["city"].tolist() == cities


def test_tsp_returns_distance_and_route():
    """Test that TSP function returns both distance and route"""
    cities = ["New York", "Boston", "Philadelphia"]
    df = create_cities_dataframe(cities, use_cache=True)
    
    distance, route = tsp(df, verbose=False)
    
    assert isinstance(distance, float)
    assert distance > 0
    assert isinstance(route, list)
    assert len(route) == 3
    assert set(route) == set(cities)


def test_analyze_convergence():
    """Test convergence analysis function"""
    # Test case: improving results
    improving = [1000, 950, 900, 880, 870, 865, 863, 862, 861, 860]
    improvement = analyze_convergence(improving, window=5)
    assert improvement is not None
    assert improvement >= 0  # Should show improvement
    
    # Test case: not enough data
    short_list = [1000, 950, 900]
    result = analyze_convergence(short_list, window=5)
    assert result is None
    
    # Test case: no improvement
    stagnant = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
    improvement = analyze_convergence(stagnant, window=5)
    assert improvement is not None
    assert abs(improvement) < 0.1  # Should show no improvement


def test_cache_operations():
    """Test cache save and load operations"""
    test_cache = {
        "TestCity": {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    }
    
    # Clean up any existing cache
    cache_file = Path("city_coordinates_cache.json")
    if cache_file.exists():
        cache_file.unlink()
    
    # Save cache
    save_cached_coordinates(test_cache)
    assert cache_file.exists()
    
    # Load cache
    loaded_cache = load_cached_coordinates()
    assert "TestCity" in loaded_cache
    assert loaded_cache["TestCity"]["latitude"] == 40.7128
    assert loaded_cache["TestCity"]["longitude"] == -74.0060
    
    # Clean up
    if cache_file.exists():
        cache_file.unlink()


def test_tsp_consistency():
    """Test that TSP returns consistent types"""
    cities = ["New York", "Boston"]
    df = create_cities_dataframe(cities, use_cache=True)
    
    # Run multiple times to check consistency
    for _ in range(3):
        distance, route = tsp(df, verbose=False)
        assert isinstance(distance, (int, float))
        assert isinstance(route, list)
        assert len(route) == len(cities)


def test_dataframe_structure():
    """Test that dataframe has correct structure"""
    cities = ["Seattle", "Portland"]
    df = create_cities_dataframe(cities, use_cache=True)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["city", "latitude", "longitude"]
    assert df["latitude"].dtype == float
    assert df["longitude"].dtype == float


def test_convergence_edge_cases():
    """Test convergence analysis edge cases"""
    # Empty list
    assert analyze_convergence([], window=5) is None
    
    # Single value
    assert analyze_convergence([1000], window=5) is None
    
    # Exactly window size
    exact_window = [1000, 950, 900, 880, 870]
    result = analyze_convergence(exact_window, window=5)
    assert result is None  # Not enough for comparison
    
    # Large improvement
    large_improvement = [10000] * 10 + [5000] * 5
    result = analyze_convergence(large_improvement, window=5)
    assert result is not None
    assert result > 40  # Should show large improvement


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
