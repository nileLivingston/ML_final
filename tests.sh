# runs RandomForest, testing different numbers of trees. this is pretty straightforward to change based on what you want to try and optimize
for i in $(seq 20 5 70); do
    java -cp /usr/share/java/weka.jar weka.classifiers.trees.RandomForest -t $1/featurization_3.arff -I $i > RandomForest/$i.txt
done

# aggregates accuracy rates
python summarize.py RandomForest