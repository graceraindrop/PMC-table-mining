import os
import json
os.chdir('/big/TextMining') #whole
xmlFolder = os.curdir + '/2015PMC' #Whole
paper_name = []
for root, dirs, files in os.walk(xmlFolder):
	for filespath in files:
		curXMLfile = os.path.join(root,filespath)
		paper_name.append(curXMLfile)

f=open('/big/bilin/table_mining/scripts/paper_names.txt','w')
json.dump(paper_name,f)
f.close()