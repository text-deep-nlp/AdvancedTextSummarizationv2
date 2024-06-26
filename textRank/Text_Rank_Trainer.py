import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import re
import io
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

encodings_to_try = ['utf-8', 'latin1', 'utf-16']

for encoding in encodings_to_try:
    try:
        df = pd.read_csv("tennis_articles.csv", encoding=encoding)
        break  # Exit the loop if the file is read successfully
    except UnicodeDecodeError:
        print(f"Failed to read using encoding: {encoding}")

# df = pd.read_csv("C:\\Users\\Atharv Chandane\\Desktop\\Text_Summarization_Extractive\\tennis_articles.csv", encoding='utf-8')

sentences = []
for s in df['article_text']:
  sentences.append(sent_tokenize(s)) 

# flatten the list
sentences = [y for x in sentences for y in x]

# remove punctuations, numbers and special characters
clean_sentences = pd.Series(sentences).str.replace("[^a-zA-Z]", " ")

# make alphabets lowercase
clean_sentences = [s.lower() for s in clean_sentences]

stop_words = stopwords.words('english')

# function to remove stopwords
def remove_stopwords(sen):
  sen_new = " ".join([i for i in sen if i not in stop_words])
  return sen_new

# remove stopwords from the sentences
clean_sentences = [remove_stopwords(r.split()) for r in clean_sentences]

# Extract word vectors
word_embeddings = {}
f = open('glove.6B.100d.txt', encoding='utf-8')
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    word_embeddings[word] = coefs
f.close()

sentence_vectors = []
for i in clean_sentences:
  if len(i) != 0:
    v = sum([word_embeddings.get(w, np.zeros((100,))) for w in i.split()])/(len(i.split())+0.001)
  else:
    v = np.zeros((100,))
  sentence_vectors.append(v)

  # similarity matrix
sim_mat = np.zeros([len(sentences), len(sentences)])

for i in range(len(sentences)):
  for j in range(len(sentences)):
    if i != j:
      sim_mat[i][j] = cosine_similarity(sentence_vectors[i].reshape(1,100), sentence_vectors[j].reshape(1,100))[0,0]

nx_graph = nx.from_numpy_array(sim_mat)
scores = nx.pagerank(nx_graph)

ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)

# Specify number of sentences to form the summary
sn = 10

# Generate summary
for i in range(sn):
  print(ranked_sentences[i][1])