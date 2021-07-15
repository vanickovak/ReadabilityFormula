from pathlib import Path
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import string
import re
import requests
from conllu import parse
import json
import random
import time

def tokenize_ud_single(text, model_language, text_is_sentences_list=True):
    if text_is_sentences_list:
        text = " ".join(text)
#use UDPipe
    url = 'http://lindat.mff.cuni.cz/services/udpipe/api/process'
    params = dict()
    params["model"] = model_language
    params["tokenizer"] = ""
    # params["tagger"] = ""
    params["output"] = "conllu"
    params["data"] = text
    response = requests.post(url, params) 
    list_of_lists_of_tokens = parse(json.loads(response.text)["result"])
    list_of_lists_of_strings = [[str(token) for token in sentence] for sentence in list_of_lists_of_tokens]

    punctuations = list(string.punctuation) # vytvoří list punct
    punctuations.append("''")
    punctuations.append("“")
    punctuations.append("„")
    punctuations.append(" ")
    punctuations.append("")
    punctuations.append("‘")
    punctuations.append("”")
    punctuations.append("–")
    punctuations.append("…")

    # Filter out the punctuations
    ret = []
    for veta in list_of_lists_of_strings:
        veta_nova = []
        for slovo in veta:
            if not slovo in punctuations:
                veta_nova.append(slovo)
        ret.append(veta_nova)
    return ret

def tokenize_ud(texts_dict, model_language):
    return { key: tokenize_ud_single(sentences_list) for key, sentences_list in texts_dict.items() }


def SentencesCounter(list_of_sentences):
    return len(list_of_sentences)

def WordCounter(list_of_sentences):
    pocet_slov= 0
    for veta in list_of_sentences:
        pocet_slov= pocet_slov+len(veta)
    return (pocet_slov)

def Flatten(list_of_sentences):
    return [item for sublist in list_of_sentences for item in sublist]

def CharacterCounter(list_of_sentences):
    pocet_znaku= 0
    for veta in list_of_sentences:
        for slovo in veta:
            pocet_znaku= pocet_znaku+len(slovo)
    return (pocet_znaku)


def SyllableCounter(list_of_words, language):
    if language == 'cs':
        return SyllableCounterCS(list_of_words)
    elif language == 'en':
        return SyllableCounterEN(list_of_words)
    elif language == 'it':
        return SyllableCounterIT(list_of_words)
    elif language == 'ru':
        return SyllableCounterRU(list_of_words)
    elif language == 'fr':
        return SyllableCounterFR(list_of_words)    
    else:
        raise Exception("Unknown language")

def SyllableCounterCS(list_of_words): 
    def count_syll(word):
        V = "[aeiuoyáéíóúůýěäëïöü]"
        word = re.sub(r"(r|l|m)\1+", r"\1", word.lower())
        word = word.replace("neuro", "nero")
        if word in ["sedm", "osm", "vosm"]:
            return 2
        elif word == "hm":
            return 1
        return len(re.findall(r"(^eu|^au|ou|{V}|(?<!{V})[rl](?!{V}))".format(V=V), word))
    syllable_count = 0
    for word in list_of_words:
        pocet=count_syll(word)
        syllable_count += pocet
    return syllable_count

def SyllableCounterEN(list_of_words): 
    def count_syll(word):
        V = "[aeiuoyäëïöü]"
        word = re.sub(r"(r|l|m)\1+", r"\1", word.lower())
        if word in ["employees", "employee", "employeed"]:
            return 3
        elif word in ["eyeing"]:
            return 2    
        return len(re.findall(r"(ou|ie|ay|oi|oo|ea|ee|ai|{V})".format(V=V), word))
    syllable_count = 0
    for word in list_of_words:
        pocet = count_syll(word)
        syllable_count += pocet
    return syllable_count


def SyllableCounterIT(list_of_words):    
    def count_syll(word):
        V = "[aeiuoyáéíóúůýěäëïöüìàùè]"
        word = re.sub(r"(r|l|m)\1+", r"\1", word.lower())
        return len(re.findall(r"(uo|ua|ia|ie|io|{V})".format(V=V), word))
    syllable_count = 0
    for word in list_of_words:
        pocet=count_syll(word)
        syllable_count += pocet
    return syllable_count


def SyllableCounterRU(list_of_words):   
    def count_syll(word):
        V = "[а, э, ы, у, о, я, е, ё, ю, и]"
        word =  word.lower()
        return len(re.findall(r"(ай|эй|ей|ий|ый|ой|уй|юй |{V})".format(V=V), word))

    syllable_count = 0
    for word in list_of_words:
        pocet=count_syll(word)
        syllable_count += pocet
    return syllable_count

def SyllableCounterFR(list_of_words):    
    def count_syll(word):
        V = "[aàâeéèêiîïoôuûyÿ]"
        word = re.sub(r"(r|l|m)\1+", r"\1", word.lower())
        if word in ["Raphaël"]:
            return 3
        if word in ["abbaye"]:
            return 3
        return len(re.findall(r"(aa|æ|ae|aë|ai|aî|aie|au|ay|aye|ée|ea|ee|eau|ei|eî|eoi|eu|eî|ey|ie|œ|oê|œu|oi|oie|oî|ou|où|oû|oue|oy|ue|üe|uy|{V})".format(V=V), word))
    syllable_count = 0
    for word in list_of_words:
        pocet=count_syll(word)
        syllable_count += pocet
    return syllable_count

def Flesch(sentences_count, words_count, syllable_count, lang):
    constants = {
        'en': {'A': 206.835, 'B': 1.015, 'C': 84.6},
        'it': {'A': 217, 'B': 1.3, 'C': 0.6 * 100 },
        'ru': {'A': 206.835, 'B': 1.3, 'C': 60.1},
        'fr': {'A': 207, 'B': 1.015, 'C': 73.6},
        'cs': {'A': 206.835, 'B': 1.672, 'C': 62.183}

    }

    if lang in constants:
        return constants[lang]['A'] - constants[lang]['B'] * (words_count/sentences_count) - constants[lang]['C'] * (syllable_count / words_count)
    return None


def FleschFromRu(sentences_count, words_count, syllable_count, lang):
    constants = {
        'en': {'A': 206.835, 'B': 1.015, 'C': 84.6},
        'it': {'A': 217, 'B': 1.3, 'C': 0.6 * 100 },
        'ru': {'A': 206.835, 'B': 1.3, 'C': 60.1},
        'fr': {'A': 207, 'B': 1.015, 'C': 73.6},
        'cs': {'A': 206.835, 'B': 1.388, 'C': 65.090}

    }

    if lang in constants:
        return constants[lang]['A'] - constants[lang]['B'] * (words_count/sentences_count) - constants[lang]['C'] * (syllable_count / words_count)
    return None

def FleschKincaid(sentences_count, words_count, syllable_count, lang):
    constants = {
        'en': {'A': 0.39, 'B': 11.8, 'C': 15.59},
        'cs': {'A': 0.52, 'B': 9.13, 'C': 16.39}
    }
    if lang in constants:
        return constants[lang]['A']  * (words_count/sentences_count) + constants[lang]['B'] * (syllable_count / words_count)- constants[lang]['C']
    return None

def ColemanLiau(sentences_count, words_count, characters_count, lang):
    constants = {
        'en': {'A': 0.0588, 'B': 0.296, 'C': 15.8},
        'cs': {'A': 0.0465, 'B': 0.286, 'C': 12.9}
    }
    if lang in constants:
        return constants[lang]['A']  * (characters_count/words_count*100) - constants[lang]['B'] * (sentences_count / words_count*100)- constants[lang]['C']
    return None

def AutomaticReadabilityIndex(sentences_count, words_count, characters_count, lang):
    constants = {
        'en': {'A': 4.71, 'B': 0.5, 'C': 21.43},
        'cs': {'A': 3.67, 'B': 0.6, 'C': 19.49}
    }
    if lang in constants:
        return constants[lang]['A']  * (characters_count/words_count) + constants[lang]['B'] * (words_count/sentences_count)- constants[lang]['C']
    return None


tabulka = {}
# if change language just here, it counts for other lang, all four formulas exist just for cs and en
lang = 'cs'
for filename in Path('.').glob('texts/*.txt'):
    file_object  = open(filename, "rb")
    text = file_object.read().decode("utf-8")
    tokenized_text = tokenize_ud_single(text, "czech", text_is_sentences_list=False)
    doc_id= str(filename)
    if doc_id not in tabulka.keys():
        tabulka[doc_id] = {}
    zaznam = {
        'sentences': SentencesCounter(tokenized_text),
        'words': WordCounter(tokenized_text),
        'syllables': SyllableCounter(Flatten(tokenized_text), lang),
        'character': CharacterCounter(tokenized_text)
    }
    zaznam['flesch'] = Flesch(zaznam['sentences'], zaznam['words'], zaznam['syllables'], lang)
#counts other version of Czech Reading Ease, which was derived from Russian data and Russian formula
    zaznam['flesch_from_ru'] = FleschFromRu(zaznam['sentences'], zaznam['words'], zaznam['syllables'], lang)
    zaznam['fleschkincaid']= FleschKincaid(zaznam['sentences'], zaznam['words'], zaznam['syllables'], lang)
    zaznam['colemanliau']= ColemanLiau(zaznam['sentences'], zaznam['words'], zaznam['character'], lang)
    zaznam['automaticreadabilityindex']= AutomaticReadabilityIndex(zaznam['sentences'], zaznam['words'], zaznam['character'], lang)
    tabulka[doc_id][lang] = zaznam

   
    with open(f"results.json", 'w') as outfile:
        json.dump(tabulka, outfile, indent=4)
