from collections import defaultdict
import operator
from lemmatizer.sllematizer import RdrLemmatizer
import nltk.data
from nltk import FreqDist
from nltk.tokenize import word_tokenize
import os

DEFAULT_SUMMARIZATION_NUMBER = 3

init_done = False

def do_init():
    global init_done
    if init_done:
        return

    init_done = True

    global lemmatizer
    this_dir = os.path.dirname(os.path.abspath(__file__))
    lemmatizer = RdrLemmatizer(os.path.join(this_dir, "lemmatizer/lem-me-sl.bin"))

    global sent_detector
    dir = os.path.join(this_dir, "tokenizers/slovene.pickle")
    sent_detector = nltk.data.load("file://" + dir)


def summarize(article_text, num_sentences=DEFAULT_SUMMARIZATION_NUMBER):
    do_init()

    # Get words from article
    words = word_tokenize(article_text)

    # Filter non-alphanumeric chars from words
    words = [filter(unicode.isalnum, word) for word in words]
    words = filter(lambda w: len(w) > 0, words)  # Remove empty words

    # Now lemmatize all words
    words = [lemmatizer.lemmatize(word).lower() for word in words]
    word_frequencies = FreqDist(words)
    most_frequent = [word[0] for word in word_frequencies.items()[:100]]

    # Now get sentences
    sentences = sent_detector.tokenize(article_text)

    wordcountdict = defaultdict(int)

    for word in most_frequent:
        lem_word = lemmatizer.lemmatize(word).lower()
        for i in range(0, len(sentences)):
            if lem_word in sentences[i]:
                wordcountdict[i] += 1

    sorted_wordcounts = sorted(wordcountdict.iteritems(), key=operator.itemgetter(1), reverse=True)[:num_sentences]
    return [sentences[num] for num, count in sorted_wordcounts]



