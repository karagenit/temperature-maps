import re

class Station:
    def __init__(self):
        self._station_id = None
        self._zipcode = None
        self._avg_daily_max_temperature = None
        self._avg_rainy_days_per_month = []
    
    @property
    def station_id(self):
        return self._station_id
    
    @station_id.setter
    def station_id(self, value):
        self._station_id = value
    
    @property
    def zipcode(self):
        return self._zipcode
    
    @zipcode.setter
    def zipcode(self, value):
        # Validate that zipcode is a 5-digit numeric string
        if not value or not re.match(r'^\d{5}$', value):
            raise ValueError("Zipcode must be a 5-digit numeric string")
        self._zipcode = value
    
    @property
    def avg_daily_max_temperature(self):
        return self._avg_daily_max_temperature
    
    @avg_daily_max_temperature.setter
    def avg_daily_max_temperature(self, value):
        if not isinstance(value, list) or len(value) != 12:
            raise ValueError("avg_daily_max_temperature must be a list with exactly 12 elements (one for each month)")
        
        # Validate that each month is a list of 31 elements
        for month_data in value:
            if not isinstance(month_data, list) or len(month_data) != 31:
                raise ValueError("Each month in avg_daily_max_temperature must be a list with exactly 31 elements (one for each day)")
        
        self._avg_daily_max_temperature = value
    
    # NOTE: the data files I think store the SUM of rainy days in a given month over 30 years, not the average like I expected. Need to divide those values by 30 (years) to get average value before setting this property.
    @property
    def avg_rainy_days_per_month(self):
        return self._avg_rainy_days_per_month
    
    @avg_rainy_days_per_month.setter
    def avg_rainy_days_per_month(self, value):
        if not isinstance(value, list) or len(value) != 12:
            raise ValueError("avg_rainy_days_per_month must be a list with exactly 12 elements (one for each month)")
        
        # Validate that each value is between 0 and 31 inclusive
        for days in value:
            if not (0 <= days <= 31):
                raise ValueError("Each value in avg_rainy_days_per_month must be between 0 and 31 inclusive")
                
        self._avg_rainy_days_per_month = value
    
    def get_temperature_score(self):
        """
        Calculate comfort score based on temperature:
        - 72°F = 40 points (optimal)
        - Points decrease with distance from 72°F
        - 32°F and 92°F = 0 points
        - Higher temperatures lose points faster
        
        Processes all valid temperature data points and returns the average score.
        """
        if self._avg_daily_max_temperature is None:
            return 0
        
        total_score = 0
        valid_days = 0
        
        for month_data in self._avg_daily_max_temperature:
            for temp_f in month_data:
                if temp_f is None:  # Skip days that don't exist (like Feb 30)
                    continue
                
                valid_days += 1
                
                if temp_f <= 72:
                    # Linear increase from 0 at 32°F to 40 at 72°F
                    day_score = (temp_f - 32) * 40 / 40 if temp_f >= 32 else 0
                else:
                    # Linear decrease from 40 at 72°F to 0 at 92°F
                    day_score = 40 - (temp_f - 72) * 40 / 20 if temp_f <= 92 else 0
                
                total_score += day_score
        
        # Return average score across all valid days
        return total_score / valid_days if valid_days > 0 else 0
    
    def get_precipitation_score(self):
        """
        Calculate precipitation score based on number of rainy days.
        10 points per day with ≥0.5" rainfall.
        
        Uses the sum of average rainy days across all months.
        """
        if not self._avg_rainy_days_per_month:
            return 0
            
        # Sum the average rainy days across all months
        total_rainy_days = sum(self._avg_rainy_days_per_month)
        # 10 points per rainy day: a rainy day at 62 or 77 equals a sunny day at 72 because I like rain
        return total_rainy_days * 10
    
    def get_total_score(self):
        """
        Calculate the total comfort score by combining temperature and precipitation scores.
        """
        temp_score = self.get_temperature_score()
        precip_score = self.get_precipitation_score()
        
        return temp_score + precip_score