import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# jsonFile = open("Data/googlescholars.json", encoding='utf-8')
interestData = json.load(open("Data/googlescholars.json", encoding='utf-8'))[5]['data']
# print(interestData)
interestDict = {}
for element in interestData:
	interestDict[element['id']] = element['name']
# print(interestDict)

a2iData = json.load(open("Data/googlescholars.json", encoding='utf-8'))[3]['data']
interestCount = {}
for element in a2iData:
	interestCount[element['Iid']] = interestCount.get(element['Iid'], 0) + 1
# interestCount = sorted(interestCount.items(), key=lambda d:d[1], reverse = True)
# print(interestCount)
# print(interestCount)
interestRank = {}
for k, v in interestDict.items():
	# print(k, v)
	interestRank[v] = interestCount.get(k)
interestRank = sorted(interestRank.items(), key=lambda d:d[1], reverse = True)
# print(interestRank[:][1])
# print(interestRank)
df = pd.DataFrame(interestRank, columns=['interest', 'num'], dtype='int64')
df = df.drop(0)
# df = df.reset_index(inplace=True, drop=True)
print(df.head(30))
plt.figure(figsize=(13,13))
graph = sns.barplot(y='interest', x='num', data = df.head(30))
for index, row in df.head(30).iterrows():
	print(row.name)
	# graph.text(row.num, row.name, row.num, color='black', ha="center")
	graph.text(row.num, row.name - 1, row.num, color='black')
# graph = df.plot(kind='barh', figsize=(10, 10))
print("processing...")
graph.figure.savefig('graph.png')
print("done!")
