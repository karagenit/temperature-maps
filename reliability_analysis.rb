# First, read through 'zipcodes-normals-stations.txt' and count how many lines start with "US"
require 'set'

def get_station_codes_set(input_file)
    us_stations = Set.new
    File.foreach(input_file) do |line|
        if line.start_with?('US')
            station_code = line.split[0]
            us_stations.add(station_code)
        end  
    end
    us_stations
end

zipcodes_stations = get_station_codes_set('zipcodes-normals-stations.txt')
puts "Number of US stations with zip code: #{zipcodes_stations.size}"

temperature_stations = get_station_codes_set('dly-tmax-normal.txt')
puts "Number of US stations tracking temperatures: #{temperature_stations.size}"

common_stations = zipcodes_stations.intersection(temperature_stations)
puts "Number of US stations with both zip code and temperature data: #{common_stations.size}"
