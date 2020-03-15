from django.test import TestCase

# Create your tests here.
a={'SyncKey': {
	'Count': 4,
	'List': [{
		'Key': 1,
		'Val': 683487370
	}, {
		'Key': 2,
		'Val': 683487812
	}, {
		'Key': 3,
		'Val': 683487678
	}, {
		'Key': 1000,
		'Val': 1569157322
	}]
}}
b=a["SyncKey"]["List"]
print(b)
import json
sysc_data_list = []
for item in a["SyncKey"]["List"]:
    temp = "%s_%s"%(item["Key"],item["Val"])
    sysc_data_list.append(temp)
sysc_data = "|".join(sysc_data_list)
print(sysc_data)

