import sys, os, re

#home_path = sys.argv[1]
#data_path = home_path + "/SentenceCorpus/labeled_articles/"
#word_lists_path = home_path + "SentenceCorpus/word_lists/"

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

def featurization_4():
	
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

	target_words.append("CITATION")
	target_words.append("NUMBER")
	target_words.append("SYMBOL")
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
	arff = open('featurization_4.arff', 'a')
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

import csv

def featurization_5():
	
	# The attributes for the .arff file.
	attributes = ['line_num', 'journal', 'expert', 'section', 'DT', 'NNP', 'NN', 'IN', 'VBZ', 'VBN', 'VBG', 'JJ', ',', 'RB', ':', 'CD', 'CC', 'PRP', 'MD', 'VB', 'NNS', 'WDT', 'VBP', 'JJR', 'TO', '``', "''", 'NNPS', 'PRP$', 'JJS', 'WRB', 'POS', 'VBD', 'EX', 'RBR', '-NONE-', 'LS', 'RBS', 'WP', 'RP', 'PDT', 'WP$', '#', '.','class']
	punc = {',':'comma', ':':'colon', '``':'opquote', "''":'closequote', '-NONE-':'none', 'WP$':'wpmoney', '#':'hashhash', '.':'periodperiod'}

	f = open('pos_csv.csv','rb')
	arff = open('featurization_5.arff','w')
	arff.write("@RELATION featurization_5\n\n")
	for a in attributes:
		if a in punc.keys():
			arff.write("@ATTRIBUTE " + punc[a] + " " + "INTEGER" + "\n")
		else:
			if a == "journal":
				data_type = "{arxiv, jdm, plos}"
			elif a == "section":
				data_type = "{abstract, introduction}"		
			elif a == "class":
				data_type = "{AIM, BASE, CONT, OWN, MISC}"
			else:
				data_type = "INTEGER"
			arff.write("@ATTRIBUTE " + a.lower() + " " + data_type + "\n")

	arff.write('\n@DATA\n')

	for line in f:
		arff.write(line)

def featurization_8():

	import nltk
	
	word_lists_path = 'SentenceCorpus/word_lists/'
	
	# The attributes for the .arff file.
	attributes = ["line_number", "num_words", "median_word_length", "mean_word_length","journal_name", "expert_annotator", "section_name"]
	poses = ['DT', 'NNP', 'NN', 'IN', 'VBZ', 'VBN', 'VBG', 'JJ', ',', 'RB', ':', 'CD', 'CC', 'PRP', 'MD', 'VB', 'NNS', 'WDT', 'VBP', 'JJR', 'TO', '``', "''", 'NNPS', 'PRP$', 'JJS', 'WRB', 'POS', 'VBD', 'EX', 'RBR', '-NONE-', 'LS', 'RBS', 'WP', 'RP', 'PDT', 'WP$', '#', '.']
	punc = {',':'comma', ':':'colon', '``':'opquote', "''":'closequote', '-NONE-':'none', 'WP$':'wpmoney', '#':'hashhash', '.':'periodperiod'}

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

	f = open("labeled_aggregate.txt", 'r')

	# To hold the cases.
	data = []
	for line in f:	
		line = line.strip('\n').split("|")
		words = re.findall(r"[\w']+", line[0])
		label = line[5]
		case = [line[1], len(words), median([len(word) for word in words]), sum([len(word) for word in words])/float(len(words)), line[2], line[3], line[4]]
		for word in target_words:
			case.append(int(word in words))
		ppos = [i[1] for i in nltk.pos_tag(nltk.word_tokenize(line[0]))]
		row = {i:0 for i in poses}
		for k in ppos:
			if k not in punc.keys():
				row[k]+=1
			

		case+=[row[i] for i in poses]
		case.append(label)			
		data.append(case)
	f.close()

	attributes += punc

	print attributes

	# Write the .arff file
	arff = open('featurization_8.arff', 'a')
	arff.write("@RELATION featurization_7\n\n")
	for a in attributes:
		if a not in punc:
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

def featurization_8():
	from nltk.stem.lancaster import LancasterStemmer
	st = LancasterStemmer()
	stopwords = ["of","a","and","the","in","to","for","that","is","on","are","with","as","by","be","an","which","it","from","or","can","have","these","has","such"] # taken from the provided txt file

	f = open("labeled_aggregate.txt")
	wordlist = []

	data = []
	for line in f:	
		line = line.strip('\n').split("|")
		words = re.findall(r"[\w']+", line[0])
		label = line[5]

		case = []
		for word in words:
			if word not in stopwords:
				if word.isalpha():
					word = word.lower()
					if len(word) > 3:
						word = st.stem(word)
					case.append(word)
					if word not in wordlist:
						wordlist.append(word)
		case.append(label)			
		data.append(case)
	f.close()
	wordlist.sort()
	
	# Write the .arff file
	arff = open('featurization_8.arff', 'a')
	arff.write("@RELATION featurization_8\n\n")
	for a in wordlist:
		arff.write("@ATTRIBUTE " + a + " " + "INTEGER" + "\n")
	arff.write("@ATTRIBUTE class_label {AIM, BASE, CONT, OWN, MISC}\n")

	arff.write("\n@DATA\n")
	for d in data:
		for a in wordlist:
			arff.write(str(int(a in d[:-1]))+",")
		arff.write(d[-1]+"\n")
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

# Done
#featurization_7()

featurization_8()
