import pytest
import sys
import os

# Add the parent directory to the path so we can import the station module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from station import Station

class TestStation:
    def test_station_initialization(self):
        station = Station()
        assert station.station_id is None
        assert station.temperature_data is None
        assert len(station.avg_rainy_days_per_month) == 0
    
    def test_station_properties(self):
        station = Station()
        station.station_id = "KNYC"
        station.temperature_data = 72
        station.avg_rainy_days_per_month = [3, 2, 4, 5, 6, 3, 2, 1, 3, 4, 5, 4]
        
        assert station.station_id == "KNYC"
        assert station.temperature_data == 72
        assert station.avg_rainy_days_per_month == [3, 2, 4, 5, 6, 3, 2, 1, 3, 4, 5, 4]
    
    def test_temperature_score_optimal(self):
        station = Station()
        station.temperature_data = 72
        assert station.get_temperature_score() == 40
    
    def test_temperature_score_cold(self):
        station = Station()
        station.temperature_data = 52
        # 52°F is 20°F below optimal (72°F)
        # Score should be (52-32)*40/40 = 20
        assert station.get_temperature_score() == 20
    
    def test_temperature_score_hot(self):
        station = Station()
        station.temperature_data = 82
        # 82°F is 10°F above optimal (72°F)
        # Score should be 40-(82-72)*40/20 = 40-20 = 20
        assert station.get_temperature_score() == 20
    
    def test_temperature_score_extreme_cold(self):
        station = Station()
        station.temperature_data = 30
        assert station.get_temperature_score() == 0
    
    def test_temperature_score_extreme_hot(self):
        station = Station()
        station.temperature_data = 95
        assert station.get_temperature_score() == 0
    
    def test_precipitation_score(self):
        station = Station()
        station.avg_rainy_days_per_month = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4]
        # Sum of rainy days = 15
        # 15 rainy days * 10 = 150
        assert station.get_precipitation_score() == 150
    
    def test_total_score(self):
        station = Station()
        station.temperature_data = 72  # Score = 40
        station.avg_rainy_days_per_month = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4]  # Score = 5
        assert station.get_total_score() == 190
    
    def test_missing_data(self):
        station = Station()
        assert station.get_temperature_score() == 0
        assert station.get_precipitation_score() == 0
        assert station.get_total_score() == 0
