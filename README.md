# Files

zipcodes-normals-stations.txt

This file maps weather stations to their zip codes and locations. Each line contains:

- A station ID (starting with "RQC")
- A zip code (like "00674")
- A location name (like "Manati")

```
RQC00666270 00674 Manati
RQC00666361 00662 Isabela
RQC00666390 00687 Morovis
RQC00666514 00783 Corozal
RQC00666805 00718 Naguabo
RQC00666900 00723 Patillas
RQC00666983 00624 Penuelas
RQC00666992 00718 Naguabo
RQC00667292 00795 Juana Diaz
RQC00667295 00716 Ponce
```

dly-tmax-normal.txt

This file contains daily maximum temperature normals (historical averages) for each day of each month at different weather stations. The format is:

- Station ID (like "AQW00061705")
- Month (like "01" for January)
- Daily temperature values for each day of the month (1-31)

The values are in tenths of degrees Fahrenheit. For example, "875C" means 87.5°F with a "C" flag indicating complete data (all 30 years were used to calculate this average).

Special values like "-8888" indicate dates that don't exist (like February 30th).

The "C" flag after each temperature indicates the data quality - in this case, "complete" meaning all 30 years of the 1981-2010 period were used to calculate the normal temperature for that day.

```
AQW00061705 01      875C   875C   875C   875C   875C   875C   875C   875C   875C   875C   876C   876C   876C   876C   876C   876C   876C   876C   876C   876C   876C   876C   876C   876C   877C   877C   877C   877C   877C   877C   877C
AQW00061705 02      878C   878C   878C   878C   878C   879C   879C   879C   879C   879C   880C   880C   880C   880C   880C   880C   881C   881C   881C   881C   881C   881C   881C   881C   882C   882C   882C   882C   882C -8888  -8888 
AQW00061705 03      882C   882C   882C   882C   882C   882C   882C   882C   882C   882C   882C   882C   882C   881C   881C   881C   881C   881C   881C   881C   881C   881C   880C   880C   880C   880C   880C   880C   879C   879C   879C
AQW00061705 04      879C   879C   878C   878C   878C   878C   878C   877C   877C   877C   877C   876C   876C   876C   876C   875C   875C   875C   874C   874C   874C   873C   873C   872C   872C   872C   871C   871C   870C   870C -8888 
AQW00061705 05      869C   869C   868C   868C   867C   867C   866C   866C   865C   865C   864C   864C   863C   863C   862C   862C   861C   861C   860C   860C   859C   859C   858C   858C   858C   857C   857C   856C   856C   855C   855C
AQW00061705 06      855C   854C   854C   853C   853C   853C   852C   852C   852C   851C   851C   851C   851C   850C   850C   850C   849C   849C   849C   849C   848C   848C   848C   848C   847C   847C   847C   846C   846C   846C -8888 
AQW00061705 07      846C   845C   845C   845C   845C   844C   844C   844C   843C   843C   843C   843C   842C   842C   842C   842C   841C   841C   841C   841C   841C   840C   840C   840C   840C   840C   840C   840C   840C   840C   840C
AQW00061705 08      840C   840C   840C   840C   840C   840C   840C   840C   841C   841C   841C   841C   842C   842C   842C   842C   843C   843C   843C   844C   844C   845C   845C   845C   846C   846C   847C   847C   847C   848C   848C
AQW00061705 09      849C   849C   849C   850C   850C   851C   851C   851C   852C   852C   852C   852C   853C   853C   853C   854C   854C   854C   854C   854C   855C   855C   855C   855C   855C   855C   856C   856C   856C   856C -8888 
AQW00061705 10      856C   856C   856C   856C   856C   857C   857C   857C   857C   857C   857C   857C   857C   857C   858C   858C   858C   858C   858C   858C   859C   859C   859C   859C   859C   860C   860C   860C   860C   861C   861C
```

The station inventories section mentions that station IDs follow a pattern where "the first two characters denote the FIPS country code, the third character is a network code that identifies the station numbering system used." So US* stations are domestic ones we care about?

US has maybe 43k zip codes (TODO verify). temp data has 90k lines (12 per station) and zip data has almost 10k. 

## Geo Shapefiles

Used for mapping. From the census bureau.

https://www.census.gov/programs-surveys/geography/technical-documentation/naming-convention/cartographic-boundary-file.html

https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2020.html#list-tab-1883739534

Got the ZIP code file from here.

## Python venv

```
python3 -m venv /Users/caleb/python/venv
source /Users/caleb/python/venv/bin/activate
python3 -m pip .....
```

## Precipitation Data

echo "Files with MLY-PRCP-AVGNDS-GE050HI: $(grep -l "MLY-PRCP-AVGNDS-GE050HI" normals-monthly/*.csv | wc -l) / Total CSV files: $(ls -1 normals-monthly/*.csv | wc -l)"
Files with MLY-PRCP-AVGNDS-GE050HI:     7484 / Total CSV files:     9839

https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc:C00823

https://noaa-normals-pds.s3.amazonaws.com/index.html#normals-monthly/1981-2010/archive/

old one 404 https://www.ncei.noaa.gov/pub/data/normals/1981-2010/

How does this have values like 120 days in january? It's like this is a sum over 30 years not an average, avg would be 4 days in jan?


## TODO

Use heat index and windchill

Use counties not zips. Use nearest station for each county.

## May 31

there's about 40k zipcodes with fairly complex shape data, makes the maps really large and not very usable.

Maybe a higher DPI png that then goes through more compression could give us better image sizes? Right now they're at 11M/18M for png/svg. That's huge and is really laggy to view. But I've seen PNGs of US maps that are less than 1MB and look great so I'm not sure what I'm doing wrong here. 

Instead I have a couple ideas. There's about 3 million square miles in the lower 48. A 10x10 mile square is 100 square miles, so there's about 30k of these. That would be fewer than the zipcodes, but probably look better and be MUCH better in the SVG because the shapes are way simpler. 

Alternatively a county map could be nice. Looks like there's about 3k counties so this would be 10x as performant as zip code shapes. 

`pytest .` to run tests.

NOAA dataset MCP to describe the data files available and how to use them?

dly-tmax-normal has 90012 lines. Which is 7501 stations (I think). normals-daily has 9840 files, so more stations. Maybe I should be using that data instead? Although that's actually just precipitation data in those files. But maybe I could download something similar for temp data? The massive .txt temp data is old stuff I downloaded a year ago but that file isn't available anymore. Maybe I can get something in the same format as precip data but for temps (ie. one CSV per station). 

## June 1

I think I'll go the route of artificially generated grid rather than based on counties, since counties tend to be fairly unevenly distributed especially more dense on the east coast. Indiana is 160 miles across (about). I feel like even a 40x40 mile grid would be acceptable. 3 million / 1600 = only 1875 elements, so probably a lot better. And I bet *almost* all of these will have a station in them, so minimal nearest-neighbor estimation is required. 

Improving finding stations within a cell: naive took minutes. Removing stations we've already found was a little better. Sorting stations by X coordinate was much better. KD tree was the best.