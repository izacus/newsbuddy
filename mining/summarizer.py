from collections import defaultdict
import operator
from lemmatizer.sllematizer import RdrLemmatizer
import nltk.data
from nltk import FreqDist
from nltk.tokenize import word_tokenize

DEFAULT_SUMMARIZATION_NUMBER = 3

def summarize(article_text, num_sentences=DEFAULT_SUMMARIZATION_NUMBER):
    # Get words from article
    words = word_tokenize(article_text)

    # Filter non-alphanumeric chars from words
    words = [filter(unicode.isalnum, word) for word in words]
    words = filter(lambda w: len(w) > 0, words)  # Remove empty words

    # Now lemmatize all words
    lemmatizer = RdrLemmatizer("lemmatizer/lem-me-sl.bin")
    words = [lemmatizer.lemmatize(word).lower() for word in words]
    word_frequencies = FreqDist(words)
    most_frequent = [word[0] for word in word_frequencies.items()[:100]]

    # Now get sentences
    sent_detector = nltk.data.load('tokenizers/punkt/slovene.pickle')
    sentences = sent_detector.tokenize(article_text)

    wordcountdict = defaultdict(int)

    for word in most_frequent:
        lem_word = lemmatizer.lemmatize(word).lower()
        for i in range(0, len(sentences)):
            if lem_word in sentences[i]:
                wordcountdict[i] += 1

    sorted_wordcounts = sorted(wordcountdict.iteritems(), key=operator.itemgetter(1), reverse=True)[:num_sentences]
    return [sentences[num] for num,count in sorted_wordcounts]



