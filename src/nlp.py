import nltk
import string
import re
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from collections import Counter

wordnet_lemmatizer = WordNetLemmatizer()
nltk.download('stopwords')
##Remove stopwords (does not contribute much in sentence)
stopword = nltk.corpus.stopwords.words('english')


def clean_text(text):
    stopword.append('hesitation')
    text_nopunct = "".join([char for char in text if char not in string.punctuation])
    tokens = word_tokenize(text_nopunct)
    tokens = [word.lower() for word in tokens]
    text = [word for word in tokens if word not in stopword]
    text = [word for word in text if len(word) > 1]
    # text = [wordnet_lemmatizer.lemmatize(word, pos="v") for word in text]

    word_counts = Counter(text).most_common()

    statistics = {}
    for word in word_counts:
        statistics[word[0]] = word[1]

    return text, statistics