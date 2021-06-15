import nltk
try:
  nltk.data.find('vader_lexicon')
except LookupError:
  nltk.download('vader_lexicon')
