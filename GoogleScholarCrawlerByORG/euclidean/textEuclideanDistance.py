import pandas as pd
import numpy as np
import nltk
nltk.download('punkt')
import sklearn
from numpy import argmax

def transform(headlines):
	tokens = [w for s in headlines for w in s ]
	print()
	print('All Tokens:')
	print(tokens)

	results = []
	label_enc = sklearn.preprocessing.LabelEncoder()
	onehot_enc = sklearn.preprocessing.OneHotEncoder()

	encoded_all_tokens = label_enc.fit_transform(list(set(tokens)))
	encoded_all_tokens = encoded_all_tokens.reshape(len(encoded_all_tokens), 1)

	onehot_enc.fit(encoded_all_tokens)

	for headline_tokens in headlines:
		print()
		print('Original Input:', headline_tokens)

		encoded_words = label_enc.transform(headline_tokens)
		print('Encoded by Label Encoder:', encoded_words)

		encoded_words = onehot_enc.transform(encoded_words.reshape(len(encoded_words), 1))
		# print('Encoded by OneHot Encoder:')
		# print(encoded_words)
		results.append(np.sum(encoded_words.toarray(), axis=0))

	return results

def euclideanDistance(str1, str2):
	str1_tokens = nltk.word_tokenize(str1)
	str2_tokens = nltk.word_tokenize(str2)

	transformed_result = transform([str1_tokens, str2_tokens])
	score = sklearn.metrics.pairwise.euclidean_distances([transformed_result[0]], [transformed_result[1]])[0][0]
	return score

s1 = "one is two ok three and my o l"
s2 = "one is two ok there and ma o l"
print(euclideanDistance(s1, s2))