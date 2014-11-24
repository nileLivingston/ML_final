import sys, os, re

home_path = sys.argv[1]
data_path = home_path + "/SentenceCorpus/labeled_articles/"
word_lists_path = home_path + "SentenceCorpus/word_lists/"

# Input:
# list - a list of numbers.
# Output:
# the median of list.
def median(list):
	list.sort()
	if len(list) % 2 == 0:
		return (list[len(list)/2] + list[(len(list)/2)-1])/float(2)
	else:
		return list[len(list)/2]

# Input:
# filename - the file path to the labeled journal file.
# Output:
# data - a list of cases, each of which follows this format:
# (Sentence, line_number, journal_name, class_label)
def aggregate(filename):
	f = open(data_path + filename, 'r')

	# The name of the journal the sentences are from.
	journal_name = filename.split("_")[0]

	# Was the labeled article annotated by a 'professional'?
	professional = int(filename.split("_")[3][0] == "3")
	
	# The sentence number, 0 indexed.
	line_num = 0

	# To hold the cases.
	data = []
	reading = ""	
	for line in f:	
		if line.strip("\n\r") == "### abstract ###":
			reading = "abstract"
			print reading
		elif line.strip("\n\r") == "### introduction ###":
			reading = "introduction"
			print reading
		else:	
			label = line[0:4]
			if label == "AIMX": label = "AIM"
			elif label == "OWNX": label = "OWN"

			words = line[4:].strip("\t\n\r")
			
			case = [words, line_num, journal_name, professional, reading, label]	
			data.append(case)		
			line_num += 1
	f.close()

	return data	

def aggregateLabeled(directory):
	# Aggregate all labeled cases into one file.
	lines = []
	for file in os.listdir(directory):
		if file.endswith(".txt"):
			lines.extend(aggregate(file))

	agg = open('labeled_aggregate.txt', 'a')
	for l in lines:
		agg.write('|'.join([str(li).strip('\n') for li in l])+"\n")
	agg.close()


def featurization_1():
	
	# The attributes for the .arff file.
	attributes = []

	# Add a new boolean attribute for each word in the word lists.
	target_words = []
	for file in os.listdir(word_lists_path):
		if file.endswith(".txt") and not file == "stopwords.txt":
			f = open(word_lists_path + file)
			for line in f:
				new_word = line.strip('\n')
				if not new_word in target_words:
					target_words.append(new_word)
			f.close()

	target_words.sort()

	for word in target_words:
		attributes.append(word)

	f = open(home_path + "labeled_aggregate.txt", 'r')

	# To hold the cases.
	data = []
	for line in f:	
		line = line.strip('\n').split("|")
		words = re.findall(r"[\w']+", line[0])	
		label = line[5]
		
		case = []
		for word in target_words:
			case.append(int(word in words))
		case.append(label)			
		data.append(case)
	f.close()

	# Write the .arff file
	arff = open('featurization_1.arff', 'a')
	arff.write("@RELATION itdoesntmatter\n\n")
	for a in attributes:
		arff.write("@ATTRIBUTE " + a + " INTEGER\n")
	arff.write("@ATTRIBUTE class_label {AIM, BASE, CONT, OWN, MISC}\n")

	arff.write("\n@DATA\n")
	for d in data:
		line = ",".join([str(di) for di in d]) + "\n"
		arff.write(line)
	arff.close()


def featurization_2():
	
	# The attributes for the .arff file.
	attributes = []

	# Add a new boolean attribute for each word in the word lists.
	target_wordlists = []
	for file in os.listdir(word_lists_path):
		if file.endswith(".txt") and not file == "stopwords.txt":
			attributes.append(file)
			wordlist = []
			f = open(word_lists_path + file)
			for line in f:
				wordlist.append(line.strip('\n'))
			f.close()
			target_wordlists.append(wordlist)


	f = open(home_path + "labeled_aggregate.txt", 'r')

	# To hold the cases.
	data = []
	for line in f:	
		line = line.strip('\n').split("|")
		words = re.findall(r"[\w']+", line[0])
		label = line[5]
		
		case = []
		for wordlist in target_wordlists:
			case.append(len(set(words).intersection(set(wordlist))))

		case.append(label)			
		data.append(case)
	f.close()

	# Write the .arff file
	arff = open('featurization_2.arff', 'a')
	arff.write("@RELATION itdoesntmatter\n\n")
	for a in attributes:
		arff.write("@ATTRIBUTE " + a + " INTEGER\n")
	arff.write("@ATTRIBUTE class_label {AIM, BASE, CONT, OWN, MISC}\n")

	arff.write("\n@DATA\n")
	for d in data:
		line = ",".join([str(di) for di in d]) + "\n"
		arff.write(line)
	arff.close()

def featurization_3():
	
	# The attributes for the .arff file.
	attributes = ["line_number", "num_words", "median_word_length", "mean_word_length","journal_name", "expert_annotator", "section_name"]

	# Add a new boolean attribute for each word in the word lists.
	target_words = []
	for file in os.listdir(word_lists_path):
		if file.endswith(".txt") and not file == "stopwords.txt":
			f = open(word_lists_path + file)
			for line in f:
				new_word = line.strip('\n')
				if not new_word in target_words:
					target_words.append(new_word)
			f.close()

	target_words.sort()

	for word in target_words:
		attributes.append(word)

	f = open(home_path + "labeled_aggregate.txt", 'r')

	# To hold the cases.
	data = []
	for line in f:	
		line = line.strip('\n').split("|")
		words = re.findall(r"[\w']+", line[0])
		label = line[5]
		
		case = [line[1], len(words), median([len(word) for word in words]), sum([len(word) for word in words])/float(len(words)), line[2], line[3], line[4]]
		for word in target_words:
			case.append(int(word in words))
		case.append(label)			
		data.append(case)
	f.close()

	# Write the .arff file
	arff = open('featurization_3.arff', 'a')
	arff.write("@RELATION itdoesntmatter\n\n")
	for a in attributes:
		if a == "journal_name":
			data_type = "{arxiv, jdm, plos}"
		elif a == "section_name":
			data_type = "{abstract, introduction}"		
		elif a == "median_word_length" or a == "mean_word_length":
			data_type = "REAL"
		else:
			data_type = "INTEGER"
		arff.write("@ATTRIBUTE " + a + " " + data_type + "\n")
	arff.write("@ATTRIBUTE class_label {AIM, BASE, CONT, OWN, MISC}\n")

	arff.write("\n@DATA\n")
	for d in data:
		line = ",".join([str(di) for di in d]) + "\n"
		arff.write(line)
	arff.close()

'''
	MAIN
'''
# Done
# aggregateLabeled(data_path)

# Done
# featurization_1()

# Done
# featurization_2()

# Done
# featurization_3()
