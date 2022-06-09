#!/usr/bin/python

import json

with open('tl_2021_06001_edges.json') as f:
	features = json.load(f)

street_blocks_from = {}
street_blocks_to = {}

for feature in features['features']:
	# skip non-roads
	if feature['properties']['MTFCC'][0] != 'S':
		continue

	# skip unnamed roads
	name = feature['properties']['FULLNAME']
	if name == '':
		continue

	# make sure assumption of LineString geometry is correct
	if feature['geometry']['type'] != 'LineString':
		die(feature['geometry']['type'])

	if name not in street_blocks_from:
		street_blocks_from[name] = {}
		street_blocks_to[name] = {}
		# identify *some* feature in each named street

	street_blocks_from[name][feature['properties']['TNIDF']] = feature
	street_blocks_to[name][feature['properties']['TNIDT']] = feature

for street in street_blocks_from:
	froms = street_blocks_from[street]
	tos = street_blocks_to[street]

	print(street)
	# there may be multiple streets with the same name, so
	# make sure we do them all
	while len(froms) > 0:
		block = list(froms)[0]
		print(block)

		# back off to the first block of this street
		while block in tos and tos[block]['properties']['TNIDF'] in froms and tos[block]['properties']['TNIDF'] != block:
			block = tos[block]['properties']['TNIDF']
			print("back off", block)

		print(street, block)
		print(list(froms))

		feat = froms[block]

		# remove the block from the available list,
		# in both directions

		del froms[block]
		if feat['properties']['TNIDT'] in tos:
			del tos[feat['properties']['TNIDT']]
