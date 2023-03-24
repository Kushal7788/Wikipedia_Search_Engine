import timeit
import xml.sax
from preprocessing import pre_process_text, pre_process_body, get_page_tokens, clear_page_tokens, return_current_tokens, \
    clear_token_counts
from dict_to_text import convert_all
from merge import merge_all
from split import split_file, store_list
from collections import Counter
import pickle
import sys
import os

index_path = ''

index_dict = dict()
title_dict = dict()
title_offset = 0
title_file = ""


def update_index_dictionaries(body_text, indx):
    global index_dict
    global title_dict
    body_dict = pre_process_body(body_text)
    page_tokens = get_page_tokens()
    title_dict[indx].append(page_tokens)
    clear_page_tokens()
    for k, v in body_dict.items():
        tokens_dict = Counter(v)
        for t_k, t_v in tokens_dict.items():
            str_val = str(indx) + ':' + str(t_v)
            if t_k in index_dict:
                if k in index_dict[t_k]:
                    index_dict[t_k][k].append(str_val)
                else:
                    index_dict[t_k][k] = [str_val]
            else:
                index_dict[t_k] = {k: [str_val]}


def update_index_title(title, page_count):
    global index_dict
    global title_dict
    global title_offset
    global title_file

    title_str_write = title + '\n'
    title_dict[page_count] = [title_offset]
    title_file.write(title_str_write)
    title_offset = title_file.tell()

    title_tokens = pre_process_text(title)
    tokens = Counter(title_tokens)
    for k, v in tokens.items():
        str_val = str(page_count) + ':' + str(v)
        if k in index_dict:
            if 't' in index_dict[k]:
                index_dict[k]['t'].append(str_val)
            else:
                index_dict[k] = {'t': [str_val]}
        else:
            index_dict[k] = {'t': [str_val]}


def index_create(file_count):
    global index_dict
    global title_dict
    file_dict = {'t': 'title_index', 'c': 'cat_index', 'e': 'external_index', 'r': 'references_index',
                 'i': 'infobox_index', 'b': 'body_index'}
    for file_key, file_name in file_dict.items():
        fp1 = open(index_path + "/index/" + file_name + "_" + str(file_count) + ".txt", "w")
        seek_ptr = 0
        for k, v in index_dict.items():
            index_write_str = ''
            if file_key in v:
                for indx, ele in enumerate(v[file_key]):
                    index_write_str += ele
                    if indx != (len(v[file_key]) - 1):
                        index_write_str += ","
                index_write_str += "\n"
                index_dict[k][file_key] = seek_ptr
                fp1.write(index_write_str)
                seek_ptr += len(index_write_str)
        fp1.close()
    fp_pickle = open("index/word_dict_" + str(file_count), "wb")
    pickle.dump(index_dict, fp_pickle)
    fp_pickle.close()
    fp_pickle = open("index/title_dict_" + str(file_count), "wb")
    pickle.dump(title_dict, fp_pickle)
    fp_pickle.close()


class WikiHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.title_flag = 0
        self.text_flag = 0
        self.title_present = False

        self.title_data = ""
        self.text_data = ""
        self.file_count = 0
        self.page_count = 1

        self.start_time = timeit.default_timer()
        self.stop_time = 0

    def startElement(self, tag, attr):
        if tag == "title":
            self.title_flag = 1
        if tag == "text":
            self.text_flag = 1

    def characters(self, content):
        if self.title_flag == 1:
            self.title_data = content

        if self.text_flag == 1:
            self.text_data += content

    def endElement(self, tag):
        global title_dict
        global index_dict
        global title_offset
        global title_file

        if tag == "title":
            self.title_flag = 0
            if len(self.title_data):
                update_index_title(self.title_data, self.page_count)
                self.title_present = True
            else:
                self.title_present = False
            self.title_data = ''

        if tag == "text":
            self.text_flag = 0
            if self.title_present:
                update_index_dictionaries(self.text_data, self.page_count)
            self.text_data = ''

        if tag == "page":
            self.page_count += 1

        if tag == "page" and self.page_count % 10000 == 0:
            total_tokens = return_current_tokens()
            if total_tokens > 60000000:
                self.stop_time = timeit.default_timer()
                print("Page Count: {0}\t Time:{1}".format(self.page_count, self.stop_time - self.start_time))
                print("Creating files: ", self.file_count)
                self.start_time = timeit.default_timer()
                index_create(self.file_count)
                clear_token_counts()
                self.page_count = 1
                self.file_count += 1
                title_dict.clear()
                index_dict.clear()
                title_offset = 0
                title_file.close()
                title_file = open(index_path + "/index/title_" + str(self.file_count) + ".txt", "w+")
                self.stop_time = timeit.default_timer()
                print("File Write Time:{0}".format(self.stop_time - self.start_time))
                self.start_time = timeit.default_timer()

        # if tag == "page" and self.page_count % 100000 == 0:
        #     self.stop_time = timeit.default_timer()
        #     print("Page Count: {0}\t Time:{1}".format(self.page_count, self.stop_time - self.start_time))
        #     self.start_time = timeit.default_timer()


def parse_file(dump_path):
    par = xml.sax.make_parser()
    handler = WikiHandler()
    par.setFeature(xml.sax.handler.feature_namespaces, 0)
    par.setContentHandler(handler)
    par.parse(dump_path)
    index_create(handler.file_count)


def compress_index():
    convert_all("word_dict_", "dict")
    convert_all("title_dict_", "list")

    merge_all("word_dict_")
    merge_all("title_dict_")

    file_list = split_file("word_dict_0", 1000000, "word_dict_fin")
    store_list("word_secondary", file_list)
    file_list = split_file("title_dict_0", 100000, "title_dict_fin")


def create_index_dir(index_path):
    if not os.path.isdir(index_path + "/index"):
        os.mkdir(index_path + "/index")


# def create_stat_file(index_path, inverted_stat):
#     total_tokens = return_tokens()
#     fp_word_dict = open(index_path + '/index/word_dict', 'rb')
#     new_dict = pickle.load(fp_word_dict)
#     unique_tokens = len(new_dict)
#     fp_word_dict.close()
#     fp_stat = open(inverted_stat + "/invertedindex_stat.txt", "w")
#     fp_stat.write(str(total_tokens) + "\n")
#     fp_stat.write(str(unique_tokens))
#     fp_stat.close()


if __name__ == "__main__":  # main
    # dump_path = sys.argv[1]
    # dump_path = os.getcwd() + "/Small_Dump/" + "small_dump.xml"
    dump_path = "/media/kushal/New Volume/IRE/Big_Dump/large.xml"
    # index_path = sys.argv[2]
    index_path = os.getcwd()
    # inverted_stat = sys.argv[3]
    inverted_stat = os.getcwd()
    create_index_dir(index_path)
    title_file = open(index_path + "/index/title_0.txt", "w+")
    start = timeit.default_timer()
    parse_file(dump_path)
    title_file.close()
    compress_index()
    stop = timeit.default_timer()
    print(stop - start)
    # create_stat_file(index_path, inverted_stat)
