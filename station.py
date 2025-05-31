class Station:
    def __init__(self):
        self._station_id = None
        self._temperature_data = None
        self._avg_rainy_days_per_month = None
    
    @property
    def station_id(self):
        return self._station_id
    
    @station_id.setter
    def station_id(self, value):
        self._station_id = value
    
    @property
    def temperature_data(self):
        return self._temperature_data
    
    @temperature_data.setter
    def temperature_data(self, value):
        self._temperature_data = value
    
    @property
    def avg_rainy_days_per_month(self):
        return self._avg_rainy_days_per_month
    
    @avg_rainy_days_per_month.setter
    def avg_rainy_days_per_month(self, value):
        self._avg_rainy_days_per_month = value
    
    def get_temperature_score(self):
        """
        Calculate comfort score based on temperature:
        - 72°F = 40 points (optimal)
        - Points decrease with distance from 72°F
        - 32°F and 92°F = 0 points
        - Higher temperatures lose points faster
        """
        if self._temperature_data is None:
            return 0
            
        temp_f = self._temperature_data
        if temp_f <= 72:
            # Linear increase from 0 at 32°F to 40 at 72°F
            return (temp_f - 32) * 40 / 40 if temp_f >= 32 else 0
        else:
            # Linear decrease from 40 at 72°F to 0 at 92°F
            return 40 - (temp_f - 72) * 40 / 20 if temp_f <= 92 else 0
    
    def get_precipitation_score(self):
        """
        Calculate precipitation score based on number of rainy days.
        10 points per day with ≥0.5" rainfall, normalized by 30.
        
        Uses the sum of average rainy days across all months.
        """
        if self._avg_rainy_days_per_month is None:
            return 0
            
        # Sum the average rainy days across all months
        total_rainy_days = sum(self._avg_rainy_days_per_month)
        return total_rainy_days * 10 / 30
    
    def get_total_score(self):
        """
        Calculate the total comfort score by combining temperature and precipitation scores.
        """
        temp_score = self.get_temperature_score()
        precip_score = self.get_precipitation_score()
        
        return temp_score + precip_score