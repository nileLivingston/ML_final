# This just makes a text file that gathers the accuracy rate. First argument is a folder with results
import glob, sys

files = glob.glob(sys.argv[1]+"/*.txt")
summary = open(sys.argv[1]+"/summary.txt","a")
for f in files:
    p = False
    summary.write(f+"\n")
    file = open(f)
    for line in file:
        if p and line.startswith("Correctly Classified Instances"):
            summary.write(line+"\n")
        if line.startswith("Correctly Classified Instances"):
            p = True
    file.close()
summary.close()
    
