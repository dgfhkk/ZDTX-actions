from prettyprinter import cpprint
from prettyprinter import pprint
from encodings import utf_8
import json
from pprint import pprint   
#read a file named "content.json"
#convert it to a dictionary
#pprint the dictionary

with open('content.json',encoding="utf-8") as f:
    data = json.load(f)
    pprint(data,indent=4,compact=True)

