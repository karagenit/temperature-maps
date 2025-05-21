# First, read through 'zipcodes-normals-stations.txt' and count how many lines start with "US"
us_count = 0
File.foreach('zipcodes-normals-stations.txt') do |line|
  us_count += 1 if line.start_with?('US')
end
puts "Number of lines starting with 'US': #{us_count}"

# Next, read through 'dly-tmax-normal.txt' and also count lines starting with US
us_count_tmax = 0
File.foreach('dly-tmax-normal.txt') do |line|
  us_count_tmax += 1 if line.start_with?('US')
end
puts "Number of lines starting with 'US' in temperature file: #{us_count_tmax}"
