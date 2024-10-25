import json

def main():
    dict = {1: [1.02,0.001], 2: [0.05, 55.9]}
 
    
    json_object = json.dumps(dict, indent = 4)
    
    with open("localData.json", "w") as outfile:
        outfile.write(json_object)
    
    with open("localData.json", "r") as infile:
        out = json.load(infile)
    print(out["2"][0])

    print(out["1"][0])   
    dict = {1: [1.69, 0.005]}
    
   
    json_object = json.dumps(dict, indent = 4)
        
    with open("localData.json", "w") as outfile:
        outfile.write(json_object)
    
    with open("localData.json", "r") as infile:
        out = json.load(infile)
    
    print(out["2"][0])
    
if __name__ == '__main__':
    main()