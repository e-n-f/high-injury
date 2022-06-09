#!/usr/bin/python

import json
import math

with open('tl_2021_06001_roads.json') as f:
	features = json.load(f)

point_instances = {}

def dist(a, b):
	dx = a[0] - b[0]
	dy = a[1] - b[1]
	scale = math.cos(a[1] * math.pi / 180.0)
	dx = dx * scale
	return math.sqrt(dx * dx + dy * dy) / .00000274 / 5280

for feature in features['features']:
	# make sure assumption of LineString geometry is correct
	if feature['geometry']['type'] != 'LineString':
		die(feature['geometry']['type'])

	# count the number of features that each point appears in,
	# because the points that appear in multiple features
	# are the intersections
	for point in feature['geometry']['coordinates']:
		p = str(point)
		if p in point_instances:
			point_instances[p] = point_instances[p] + 1
		else:
			point_instances[p] = 1

for feature in features['features']:
	geom = feature['geometry']['coordinates']

	i = 0
	while i < len(geom):
		total = 0

		# walk forward until there is at least a quarter mile
		for j in range(i + 1, len(geom)):
			total = total + dist(geom[j - 1], geom[j])
			if total >= 0.25:
				break

		# continue walking forward while not at an intersection
		while j < len(geom) and point_instances[str(geom[j])] == 1:
			total = total + dist(geom[j - 1], geom[j])
			j = j + 1

		# skip streets that cannot be extended 0.25 miles from their origin
		if (i == 0 or j == len(geom)) and total < 0.25:
			break

		obj = {
			'type': 'Feature',
			'properties': {
				'name': feature['properties']['FULLNAME'],
				'start': i,
				'end': j,
				'distance': total
			},
			'geometry': {
				'type': 'LineString',
				'coordinates': []
			}
		}

		for k in range(i, j):
			obj['geometry']['coordinates'].append(geom[k])

		print(json.dumps(obj))

		# walk i forward to the next intersection too:
		i = i + 1
		while i < len(geom) and point_instances[str(geom[i])] == 1:
			i = i + 1
