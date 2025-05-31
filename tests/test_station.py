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
        assert station.avg_daily_max_temperature is None
        assert len(station.avg_rainy_days_per_month) == 0
    
    def test_station_properties(self):
        station = Station()
        station.station_id = "KNYC"
        # Create a 12x31 array of temperatures (one per month, 31 days each)
        temp_data = [[72 for _ in range(31)] for _ in range(12)]
        station.avg_daily_max_temperature = temp_data
        station.avg_rainy_days_per_month = [3, 2, 4, 5, 6, 3, 2, 1, 3, 4, 5, 4]
        
        assert station.station_id == "KNYC"
        assert station.avg_daily_max_temperature == temp_data
        assert station.avg_rainy_days_per_month == [3, 2, 4, 5, 6, 3, 2, 1, 3, 4, 5, 4]
    
    def test_avg_daily_max_temperature_validation_length(self):
        station = Station()
        with pytest.raises(ValueError, match="must be a list with exactly 12 elements"):
            station.avg_daily_max_temperature = [[72 for _ in range(31)] for _ in range(10)]
    
    def test_avg_daily_max_temperature_validation_month_length(self):
        station = Station()
        invalid_data = [[72 for _ in range(31)] for _ in range(11)]
        invalid_data.append([72 for _ in range(25)])  # Last month has only 25 days
        with pytest.raises(ValueError, match="must be a list with exactly 31 elements"):
            station.avg_daily_max_temperature = invalid_data
    
    def test_avg_rainy_days_validation_length(self):
        station = Station()
        with pytest.raises(ValueError, match="must be a list with exactly 12 elements"):
            station.avg_rainy_days_per_month = [1, 2, 3]
    
    def test_avg_rainy_days_validation_min_value(self):
        station = Station()
        with pytest.raises(ValueError, match="must be between 0 and 31 inclusive"):
            station.avg_rainy_days_per_month = [1, 2, -1, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    
    def test_avg_rainy_days_validation_max_value(self):
        station = Station()
        with pytest.raises(ValueError, match="must be between 0 and 31 inclusive"):
            station.avg_rainy_days_per_month = [1, 2, 32, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    
    def test_avg_rainy_days_valid_boundary_values(self):
        station = Station()
        # Test with boundary values (0 and 31)
        station.avg_rainy_days_per_month = [0, 31, 15, 20, 10, 5, 8, 12, 18, 22, 25, 30]
        assert station.avg_rainy_days_per_month == [0, 31, 15, 20, 10, 5, 8, 12, 18, 22, 25, 30]
    
    def test_temperature_score_optimal(self):
        station = Station()
        # All days at optimal temperature (72°F)
        temp_data = [[72 for _ in range(31)] for _ in range(12)]
        station.avg_daily_max_temperature = temp_data
        assert station.get_temperature_score() == 40
    
    def test_temperature_score_cold(self):
        station = Station()
        # All days at 52°F
        temp_data = [[52 for _ in range(31)] for _ in range(12)]
        station.avg_daily_max_temperature = temp_data
        # 52°F is 20°F below optimal (72°F)
        # Score should be (52-32)*40/40 = 20
        assert station.get_temperature_score() == 20
    
    def test_temperature_score_hot(self):
        station = Station()
        # All days at 82°F
        temp_data = [[82 for _ in range(31)] for _ in range(12)]
        station.avg_daily_max_temperature = temp_data
        # 82°F is 10°F above optimal (72°F)
        # Score should be 40-(82-72)*40/20 = 40-20 = 20
        assert station.get_temperature_score() == 20
    
    def test_temperature_score_extreme_cold(self):
        station = Station()
        # All days at 30°F
        temp_data = [[30 for _ in range(31)] for _ in range(12)]
        station.avg_daily_max_temperature = temp_data
        assert station.get_temperature_score() == 0
    
    def test_temperature_score_extreme_hot(self):
        station = Station()
        # All days at 95°F
        temp_data = [[95 for _ in range(31)] for _ in range(12)]
        station.avg_daily_max_temperature = temp_data
        assert station.get_temperature_score() == 0
    
    def test_temperature_score_with_none_values(self):
        station = Station()
        # Create data with some None values (like Feb 30)
        temp_data = [[72 for _ in range(31)] for _ in range(12)]
        # Set some days to None
        temp_data[1][28] = None  # Feb 29
        temp_data[1][29] = None  # Feb 30
        temp_data[1][30] = None  # Feb 31
        temp_data[3][30] = None  # Apr 31
        station.avg_daily_max_temperature = temp_data
        # Should still be 40 since all valid days are at 72°F
        assert station.get_temperature_score() == 40
    
    def test_temperature_score_mixed_temperatures(self):
        station = Station()
        # Create data with mixed temperatures
        temp_data = [
            [72 for _ in range(31)],  # Jan - all optimal
            [52 for _ in range(31)],  # Feb - all cold
            [82 for _ in range(31)],  # Mar - all hot
        ]
        # Fill the rest with optimal temperature
        for i in range(9):
            temp_data.append([72 for _ in range(31)])
        
        # Set some days to None
        temp_data[1][28] = None  # Feb 29
        temp_data[1][29] = None  # Feb 30
        temp_data[1][30] = None  # Feb 31
        
        station.avg_daily_max_temperature = temp_data
        
        # Expected score: (31*40 + 28*20 + 31*20 + 9*31*40) / (31 + 28 + 31 + 9*31)
        # = (1240 + 560 + 620 + 11160) / (31 + 28 + 31 + 279)
        # = 13580 / 369 ≈ 36.8
        expected_score = (31*40 + 28*20 + 31*20 + 9*31*40) / (31 + 28 + 31 + 9*31)
        assert abs(station.get_temperature_score() - expected_score) < 0.1
    
    def test_precipitation_score(self):
        station = Station()
        station.avg_rainy_days_per_month = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4]
        # Sum of rainy days = 15
        # 15 rainy days * 10 = 150
        assert station.get_precipitation_score() == 150
    
    def test_total_score(self):
        station = Station()
        # All days at optimal temperature (72°F)
        temp_data = [[72 for _ in range(31)] for _ in range(12)]
        station.avg_daily_max_temperature = temp_data  # Score = 40
        station.avg_rainy_days_per_month = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4]  # Score = 150
        assert station.get_total_score() == 190
    
    def test_missing_data(self):
        station = Station()
        assert station.get_temperature_score() == 0
        assert station.get_precipitation_score() == 0
        assert station.get_total_score() == 0
