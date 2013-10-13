from collections import defaultdict
import operator
from lemmatizer.sllematizer import RdrLemmatizer
import nltk.data
from nltk import FreqDist
from nltk.tokenize import word_tokenize
import os

DEFAULT_SUMMARIZATION_NUMBER = 3


class Summarizer():

    def __init__(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.lemmatizer = RdrLemmatizer(os.path.join(this_dir, "lemmatizer/lem-me-sl.bin"))
        dir = os.path.join(this_dir, "tokenizers/slovene.pickle")
        self.sent_detector = nltk.data.load("file://" + dir)

        self.stopwords = open(os.path.join(this_dir, "tokenizers/stopwords.txt"), "rb").read().splitlines()
        self.stopwords = filter(lambda w: not w.startswith("#"), self.stopwords)
        # Convert to unicode
        self.stopwords = [word.decode("utf-8") for word in self.stopwords]

    def summarize(self, article_text, num_sentences=DEFAULT_SUMMARIZATION_NUMBER):

        # Get words from article
        words = word_tokenize(article_text)

        # Filter non-alphanumeric chars from words
        words = [filter(unicode.isalnum, word) for word in words]
        words = filter(lambda w: len(w) > 0, words)  # Remove empty words

        # Now lemmatize all words
        words = [self.lemmatizer.lemmatize(word).lower() for word in words if word.lower() not in self.stopwords]
        word_frequencies = FreqDist(words)
        most_frequent = [word[0] for word in word_frequencies.items()[:100]]

        # Now get sentences
        sentences = self.sent_detector.tokenize(article_text)

        wordcountdict = defaultdict(int)

        for word in most_frequent:
            lem_word = self.lemmatizer.lemmatize(word).lower()
            for i in range(0, len(sentences)):
                if lem_word in sentences[i]:
                    wordcountdict[i] += 1

        sorted_wordcounts = sorted(wordcountdict.iteritems(), key=operator.itemgetter(1), reverse=True)[:num_sentences]
        return [sentences[num] for num, count in sorted_wordcounts]



