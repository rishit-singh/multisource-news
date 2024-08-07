import os
import sys
import json

lookup = {} 

with open(sys.argv[1], 'r') as fp:
    j = json.loads(fp.read())  
    
    for key in j:
        words = " ".join(key["keywords"])
        
        if not words in lookup:
            lookup[words] = words
    with open(sys.argv[2], 'w') as fp1:
        fp1.write(json.dumps([keyword for keyword in lookup], indent=2))
    
