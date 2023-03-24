import re
from nltk import word_tokenize
from Stemmer import Stemmer
from nltk.corpus import stopwords
from collections import defaultdict
import nltk
import timeit

# nltk.download('punkt')
# stemmer = Stemmer.Stemmer('english')
# stemmer = Stemmer('porter')
stopwords = set(stopwords.words('english'))
stopword_dict = defaultdict(int)
for word in stopwords:
    stopword_dict[word] = 1

token_counts = 0
page_token_counts = 0


def clear_page_tokens():
    global page_token_counts
    page_token_counts = 0


def get_page_tokens():
    global page_token_counts
    return page_token_counts


def return_current_tokens():
    global token_counts
    return token_counts


def clear_token_counts():
    global token_counts
    token_counts = 0


def remove_links(text):
    text = re.sub(r'http\S+', "", text)
    return text


def remove_punctuations(text):
    text = re.sub(r'[^\w\s]', '', text)
    return text


def tokenize(text, stemming=True):
    global page_token_counts
    global token_counts
    words = word_tokenize(text.lower())
    tokens = [i for i in words if i not in stopword_dict and 1 < len(i) < 15]

    # for ele in words:
    #     if ele not in stopword_dict and len(ele) > 1 and len(ele) < 15:
    #         tokens.append(stemmer.stemWord(ele))
    # tokens.append(ele)

    token_counts += len(words)
    page_token_counts += len(tokens)
    return tokens


def pre_process_text(text, stemming=True):
    text = remove_links(text)
    text = remove_punctuations(text)
    words = tokenize(text, stemming)

    return words


def get_infobox(text):
    pattern = re.compile(r'\{Infobox')
    info_splits = pattern.split(text)
    pattern_2 = re.compile(r'\}\}\n(\w|\'|\n)')
    info_list = []
    final = []
    if len(info_splits) > 1:
        for ele in info_splits[1:]:
            info_box_data = pattern_2.split(ele)[0]
            text = text.replace(info_box_data, '')
            info_list.append(info_box_data)
        for ele in info_list:
            for line in ele.split('\n'):
                if len(line) and line[0] == '|':
                    value = line.split("=")
                    if len(value) > 1:
                        for info_word in value[1:]:
                            final += pre_process_text(info_word)
                elif len(line):
                    final.extend(pre_process_text(line))
    text = pattern.sub("", text)
    return text, final


def get_categories(text):
    cat_tokens = []
    pattern = re.compile(r'(\[\[Category:)(.*)(\]\])')
    cat_list = pattern.findall(text)
    for cat in cat_list:
        cat_tokens.extend(pre_process_text(cat[1]))
    text = pattern.sub('', text)
    return text, cat_tokens


def get_references(text):
    pattern = re.compile(r'==References==|== References ==|== References==|==References ==')
    ref_list_brk = pattern.split(text)
    ref_list = []
    text = pattern.sub("", text)
    if len(ref_list_brk) > 1:
        residue_ref_list = ref_list_brk[1].split("\n")
        for ele in residue_ref_list[2:]:
            if len(ele) and ele[0] != '*':
                break
            if len(ele):
                ref_list.extend(pre_process_text(ele))
                text = text.replace(ele, '')
    return text, ref_list


def get_external_links(text):
    pattern = re.compile(r'==External links==|== External links ==|== External links==|==External links ==')
    ext_list_brk = pattern.split(text)
    ext_list = []
    text = pattern.sub("", text)
    if len(ext_list_brk) > 1:
        residue_ext_list = ext_list_brk[1].split("\n")
        for ele in residue_ext_list[2:]:
            if len(ele) and ele[0] != '*':
                break
            if len(ele):
                ext_list.extend(pre_process_text(ele))
                text = text.replace(ele, '')
    return text, ext_list


def pre_process_body(text):
    text, info_list = get_infobox(text)
    text, cat_list = get_categories(text)
    text, ref_list = get_references(text)
    text, ext_list = get_external_links(text)
    text = text[:int(len(text) * 0.45)]
    body_list = pre_process_text(text, True)

    # print("Infobox: {}".format(info_list))
    # print("Categories: {}".format(cat_list))
    # print("References: {}".format(ref_list))
    # print("External Links: {}".format(ext_list))
    # print("Body: {0} {1}".format(len(body_list), body_list))

    body_dict = dict()
    body_dict['i'] = info_list
    body_dict['c'] = cat_list
    body_dict['r'] = ref_list
    body_dict['e'] = ext_list
    body_dict['b'] = body_list

    return body_dict
