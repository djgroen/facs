import csv
import sys
import pprint
import yaml
import random

# File to read in CSV files of building definitions.
# The format is as follows:
# No,building,Longitude,Latitude,Occupancy
#lids = {"park":0,"hospital":1,"supermarket":2,"office":3,"school":4,"leisure":5,"shopping":6}

pp = pprint.PrettyPrinter()

def apply_building_mapping(mapdict, label):
  """
  Applies a building map YAML to a given label, binning it
  into the appropriate category.
  """
  for category in mapdict:
    #print(mapdict, category, label)
    if label in mapdict[category]['labels']:
      return category
  return "house"

def read_building_csv(e, csvfile, building_type_map="covid_data/building_types_map.yml", house_ratio=1, workspace=12, office_size=1600, household_size=2.6, work_participation_rate=0.5, dumptypesandquit=False, dumpnearest=False):
  """
  house_ratio = number of households per house.
  workspace = m2 of office space per worker.
  office_size = average office size per building.
  household_size = average size of household.
  work_participation_rate = fraction of population that works.
  """

  e.household_size = household_size

  building_mapping = {}
  with open(building_type_map) as f:
    building_mapping = yaml.safe_load(f)

  house_csv_count = 0

  if csvfile == "":
    print("Error: could not find csv file.")
    sys.exit()
  with open(csvfile) as csvfile:
    building_reader = csv.reader(csvfile)
    row_number = 0
    num_locs = 0
    num_houses = 0
    office_sqm = 0
    building_types = {}
    xbound = [99999.0,-99999.0]
    ybound = [99999.0,-99999.0]

    for row in building_reader:
      if row_number == 0:
        row_number += 1
        continue
      x = float(row[1])
      y = float(row[2])
      xbound[0] = min(x,xbound[0])
      ybound[0] = min(y,ybound[0])
      xbound[1] = max(x,xbound[1])
      ybound[1] = max(y,ybound[1])

      location_type = apply_building_mapping(building_mapping, row[0])
      sqm = int(row[3])

      #count all the building types in a dict.
      if row[0] not in building_types:
        building_types[row[0]] = 1
      else:
        building_types[row[0]] += 1

      if location_type == "house":
        if house_csv_count % house_ratio == 0:
          if num_houses % e.size == e.rank:
            e.addHouse(num_houses, x , y, house_ratio)

          num_houses += 1
        house_csv_count += 1
      else:
        #e.addLocation(num_locs, location_type, x, y, building_mapping[location_type]['default_sqm'])
        if location_type == "office":
          pass
          #num_locs += 1
          #office_sqm += sqm
          #e.addLocation(num_locs, location_type, x, y, sqm*10) # multiply office sqm by 10 to compensate for lack of parsing.
          # Space should be about 1 million m2 per borough, https://www.savoystewart.co.uk/blog/office-floor-space-in-london-growing-despite-premium-cost
        else:
          num_locs += 1
          e.addLocation(num_locs, location_type, x, y, sqm)
      row_number += 1
      if row_number % 10000 == 0:
        print(row_number, "read", file=sys.stderr)
    print(row_number, "read", file=sys.stderr)
    print("bounds:", xbound, ybound, file=sys.stderr)
    office_sqm = workspace*house_csv_count*work_participation_rate # 10 sqm per worker, 2.6 person per household, 50% in workforce
    office_sqm_red = office_sqm
    
    f = open("offices.csv","w")
    while office_sqm_red > 0:
      num_locs += 1
      e.addRandomOffice(f, num_locs, xbound, ybound, office_size)
      #x = random.uniform(xbound[0],xbound[1])
      #y = random.uniform(ybound[0],ybound[1])
      #e.addLocation(num_locs, "office", x, y, office_size)
      #f.write("office,{},{},{}\n".format(x, y, office_size))

      office_sqm_red -= office_size


  print("Read in {} houses and {} other locations.".format(num_houses, num_locs))
  print("Office sqm = {}".format(office_sqm))
  print("Type distribution:")
  print("house",len(e.houses))
  e.init_loc_inf_minutes()
  print("raw types are:")
  pp.pprint(building_types)

  e.update_nearest_locations(dumpnearest)
  if dumptypesandquit:
    sys.exit()

