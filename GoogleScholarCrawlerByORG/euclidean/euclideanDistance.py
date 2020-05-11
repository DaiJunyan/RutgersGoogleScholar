import pandas as pd
import numpy as np
import json
import os

list_totalInterest = json.load(open("Data/googlescholars.json", encoding='utf-8'))[5]['data']
dict_totalInterest = {}
for element in list_totalInterest:
	dict_totalInterest[element['id']] = element['name']
# print(dict_totalInterest)

list_totalAuthor = json.load(open("Data/googlescholars.json", encoding='utf-8'))[2]['data']
dict_totalAuthor = {}
for element in list_totalAuthor:
	dict_totalAuthor[element['id']] = element['name']
# print(dict_totalAuthor)
# print(dict_totalAuthor.get('-1'))


list_A2I = json.load(open("Data/googlescholars.json", encoding='utf-8'))[3]['data']
dict_A2I = {}
for element in list_A2I:
	if(dict_A2I.get(element['Aid']) is None):
		dict_A2I[element['Aid']] = [element['Iid']]
	else:
		dict_A2I[element['Aid']] += [element['Iid']]

# print(dict_A2I)
if (not os.path.exists("Data/input_df.json")):
	print("File input_df.json does not exist. Generating...")
	dict_input_data = {}
	for k, v in dict_A2I.items():
		dict_input_data[dict_totalAuthor.get(k)] = []
		# print(v)
		for element in dict_totalInterest:
			if(element in v):
				dict_input_data[dict_totalAuthor.get(k)] += [1]
			else:
				dict_input_data[dict_totalAuthor.get(k)] += [0]
	# print(dict_input_data)
	df = pd.DataFrame.from_dict(dict_input_data, orient='index', columns=list(dict_totalInterest.values()))
	print("done!")
	
	print("exporting dataframe...")
	df.to_json(r'Data/input_df.json')
	print("done!")
else:
	print("File input_df.json detected! Reading...")
	df = pd.read_json(r'Data/input_df.json')
	print("done!")
print(df)

def Euclidean_Dist(df1, df2, cols=list(dict_totalInterest.values())):
	return np.linalg.norm(df1[cols].values - df2[cols].values, axis=0)

if(not os.path.exists("Data/euclideanDistanceDF.json")):
	print("File euclideanDistanceDF.json does not exist. Generating...")
	euclidean_dict = {}
	for i in range(len(df)):
		print("processing the", (i + 1), "th author:")
		for j in range(i+1, len(df)):
			index_name = str(len(euclidean_dict) + 1)
			euclideanValue = Euclidean_Dist(df.iloc[i], df.iloc[j])
			print("\tEuclidean Value between %d and %d: %f" %(i+1, j+1, euclideanValue))
			euclidean_dict[index_name] = [df.index[i], df.index[j], euclideanValue]

	euclideanDistanceDF = pd.DataFrame.from_dict(euclidean_dict, orient='index', columns=['Author 1', 'Author 2', 'Euclidean Distance'])
	print("done!")

	print("exporting dataframe...")
	euclideanDistanceDF.to_json(r'Data/euclideanDistance.json')
	print("done!")
else:
	print("File euclideanDistanceDF.json detected! Reading...")
	euclideanDistanceDF = pd.read_json(r'Data/euclideanDistanceDF.json')
	print("done!")
print(euclideanDistanceDF)


# df1 = pd.DataFrame({'user_id':[1,2,3],
#                 'x_coord':[1,2,3],
#                 'y_coord':[1,2,3]})

# df2 = pd.DataFrame({'user_id':[0],
#                 'x_coord':[0],
#                 'y_coord':[0]})
# print(df1.loc[0:1])
# print(df1)
# print(df1['user_id'].count())
# print(type(df1.iloc[0]))
# # print(df2)
# print(type(Euclidean_Dist(df1.iloc[0], df1.iloc[1])))
# print(Euclidean_Dist(df1.iloc[0], df1.iloc[1]))
# print(Euclidean_Dist(df1, df2))