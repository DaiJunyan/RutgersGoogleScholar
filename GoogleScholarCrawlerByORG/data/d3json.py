import pymysql
import pandas as pd

connect = pymysql.connect(
			host = 'localhost',
			db = 'GoogleScholars',
			user = 'root',
			passwd = '')
cur = connect.cursor()

# select Iid where Iid in frequent_itemsets
df = pd.read_json('frequent_itemsets.json')
df1 = df[(df['length']==1) & (df['support']>0.0150)]['itemsets']
itemlist = []
for row in list(df1):
    itemlist.append(row[0])
cur.execute('''SELECT id, name from interests''')
freqiList = []
for row in cur:
    if str(row[1]) not in itemlist: continue
    freqiList.append(int(row[0]))

cur.execute('''SELECT DISTINCT Aid, name, Iid
				FROM authors_to_interests 
				INNER JOIN authors 
				on authors_to_interests.Aid = authors.id
				WHERE Iid != 18''')

print("Starting...")

fhand = open('freq_nodes_links.js','w', encoding='utf-8')
fhand.write('freq_nodes_linksJson={"nodes":[\n')
count = 0
imap = dict()
for row in cur:
	if int(row[2]) not in freqiList: continue # only include authors with interests in frequent_itemsets
	if row[0] in imap: continue # avoid duplicate authors
	if count > 0 : fhand.write(',\n')
	fhand.write('{'+'"name":"'+str(row[1])+'","id":'+str(row[0])+'}')
	imap[row[0]] = count
	count = count + 1
	# if count > 20: break
fhand.write('],\n')
print(count)

cur.execute('''SELECT a.Aid, b.Aid
				FROM authors_to_interests a JOIN authors_to_interests b
				ON a.Iid = b.Iid WHERE a.Aid != b.Aid AND a.Iid!=18''')
fhand.write('"links":[\n')

count = 0
links = list()
for row in cur:
	if row[0] not in imap or row[1] not in imap : continue
	id0 = imap[row[0]]
	id1 = imap[row[1]]
	if (id1, id0) in links: continue
	if count > 0: fhand.write(',\n')
	fhand.write('{"source":' + str(imap[row[0]]) + ',"target":' + str(imap[row[1]]) + ',"value":3}')
	links.append(tuple((id0,id1)))
	count = count + 1

fhand.write(']};')
fhand.close()
cur.close()

print("Done.")