import json
import binascii
import pandas as pd
import os
import sys

#This is the path for the layout file that is being read
filename = "Report_Layout_justin"

#this opens the file and cleans out any non ASCII text (<0x00>)
with open(os.path.join(sys.path[0], filename), "r") as f:
	text = f.read()
	
	basetext = ""
	for x in text:
		if ord(x) == 0:
			dummy=1
		else:
			basetext = basetext+x

#create dataframe to store all fields in the report
data = []


#function to parse through and identify visuals on the power bi report
def visualparser(pagename,jsonVisual):
	
	#get visual type
	visualType = jsonVisual['config']["singleVisual"]["visualType"]
	#print(jsonVisual)
	#print("")
	#print("Visual Type: " + visualType)

	#get visual ID
	visualID = jsonVisual['config']['name']
	#print(visualID)

	#iterates through the visual dynamically pull all fields out ({y,x,category,value} field types in the visual)
	def visualreader(x):
		for key in x:
			for y in x[key]:
				#print("FIELD: " + y['queryRef'])
				data.append([pagename,visualID,visualType,key,y['queryRef']])


	#executes the visualreader()
	visualreader(jsonVisual['config']['singleVisual']['projections'])


#find all matching brackets to clean and identify visuals in the report
def find_brackets(s,open,close):
    toret = {}
    pstack = []

    for i, c in enumerate(s):
        if c == open:
            pstack.append(i)
        elif c == close:
            if len(pstack) == 0:
                raise IndexError("No matching closing brackets at: " + str(i))
            toret[pstack.pop()] = i

    if len(pstack) > 0:
        raise IndexError("No matching opening brackets at: " + str(pstack.pop()))

    return toret

'''
LEGACY CODE. NEW CODE ATTACHES THE PAGE NAME ASSOCIATED WITH THE VISUAL

#where that magic happens. I put together all matching brackets identified and fill them in with the corresponding text. I fo
list = find_brackets(basetext,'{','}')
for key, value in list.items():
	if basetext[key:value+1] != "{}":
		configcheck = "\"config\":\"" + basetext[key:value+1]
		
		if (basetext.find(configcheck) != -1):
			visualjson = "{" + configcheck.replace("\\","") + "}"
			cleanedjson = visualjson.replace("\"{","{").replace("}\"","}").replace("'\"","").replace("\"'","").replace("Top","\"Top\"")
			#print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')


			if cleanedjson.find("themeCollection") == -1:
				jsonvisual = json.loads(cleanedjson)
				#visualparser(jsonvisual)

'''

#resulting DataFrame
#VisualTable = pd.DataFrame(data, columns=['Visual ID','Visual Type', 'Field Category','Field Name'])
#VisualTable.to_csv(path_or_buf = "test.csv", index=False)


#print(VisualTable)





#find pages and vsuals within pages
list = find_brackets(basetext,'[',']')
for key, value in list.items():
	if basetext[key:value+1] != "[]":
		sectionscheck = "\"sections\":" + basetext[key:value+1]

		if (basetext.find(sectionscheck) != -1):
			visualjson = "{" + sectionscheck.replace("\\","") + "}"
			cleanedjson = visualjson.replace("\"{","{").replace("}\"","}").replace("'\"","").replace("\"'","").replace("Top","\"Top\"")
			#print(cleanedjson)
			pagesjson = json.loads(cleanedjson)

			sectionlist = pagesjson['sections']
			
			for page in sectionlist:
				pagename = page['displayName']
				#print(pagename)
				#print(page)
				#print(page['visualContainers'])

				for visual in page['visualContainers']:
					#print(visual['config'])
					visualparser(pagename,visual)
					#print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')

				#print('|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')


VisualTable = pd.DataFrame(data, columns=['Page Name','Visual ID','Visual Type', 'Field Category','Field Name'])
VisualTable.to_csv(path_or_buf = "test.csv", index=False)


print(VisualTable)