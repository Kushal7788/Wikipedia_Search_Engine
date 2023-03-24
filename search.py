from preprocessing import pre_process_text
import timeit
import sys
import os

index_path = "index/"
dict_path = "final/"

out_file = ""


def get_batch_count():
    dir_list = os.listdir(index_path)
    return int(len(dir_list) / 9)


def process_title_freq(title_freq):
    title_freq_list = title_freq.split(",")
    return title_freq_list


def extract_title_id(title_freq_list, res_title_dict, batch_number, score_mult):
    for ele in title_freq_list:
        title_id, score_val = ele.split(":")
        score_val = int(score_val)
        if title_id + "_" + str(batch_number) in res_title_dict:
            res_title_dict[title_id + "_" + str(batch_number)] += score_val * score_mult
        else:
            res_title_dict[title_id + "_" + str(batch_number)] = score_val * score_mult
    return res_title_dict


def extract_title_info(str_val):
    final_dict = dict()
    word, info = str_val.split("-")
    files = info.split(",")
    file_dict = dict()
    for ele in files:
        file_num, pointers = ele.split(":")
        pointer_dict = []
        for indx, sub_ele in enumerate(pointers.split(" ")):
            if sub_ele[0] != "n":
                pointer_dict.append(int(sub_ele))
        file_dict[int(file_num)] = pointer_dict
    final_dict[word] = file_dict
    return final_dict


def sort_dict(res_titles):
    res_titles = {k: v for k, v in sorted(res_titles.items(), key=lambda item: item[1], reverse=True)}
    return res_titles


def extract_word_info(str_val):
    final_dict = dict()
    rev_arr_map = {0: 'b', 1: 't', 2: 'e', 3: 'c', 4: 'i', 5: 'r'}
    word, info = str_val.split("-")
    files = info.split(",")
    file_dict = dict()
    for ele in files:
        file_num, pointers = ele.split(":")
        pointer_dict = dict()
        for indx, sub_ele in enumerate(pointers.split(" ")):
            if sub_ele[0] != "n":
                pointer_dict[rev_arr_map[indx]] = int(sub_ele)
        file_dict[int(file_num)] = pointer_dict
    final_dict[word] = file_dict
    return final_dict


def get_element(path, ele, mode_type="str"):
    fp = open(index_path + dict_path + path, "r")
    line = fp.readline()
    while line:
        k1, v1 = line.split("-")
        if mode_type == "str":
            if k1 == ele:
                fp.close()
                return line
        elif mode_type == "int":
            if int(k1) == ele:
                fp.close()
                return line
        line = fp.readline()
    fp.close()
    return None


def get_result(token, ele, res_titles, field="all"):
    global index_path
    word_dict = extract_word_info(token)
    file_dict = {'t': 'title_index_', 'c': 'cat_index_', 'e': 'external_index_', 'r': 'references_index_',
                 'i': 'infobox_index_', 'b': 'body_index_'}
    score_mult = {'t': 0.75, 'c': 0.8, 'i': 0.65, 'r': 0.4, 'e': 0.4, 'b': 0.00001}
    search_dict = word_dict[ele]
    for k, v in search_dict.items():
        index_dict = v
        if field == "all":
            for ind_k, ind_v in index_dict.items():
                fp = open(index_path + file_dict[ind_k] + str(k) + ".txt", "r")
                fp.seek(ind_v)
                title_freq = fp.readline()
                fp.close()
                title_freq_list = process_title_freq(title_freq)
                res_titles = extract_title_id(title_freq_list, res_titles, k, score_mult[ind_k])
        else:
            if field in index_dict:
                fp = open(index_path + file_dict[field] + str(k) + ".txt", "r")
                fp.seek(index_dict[field])
                title_freq = fp.readline()
                fp.close()
                title_freq_list = process_title_freq(title_freq)
                res_titles = extract_title_id(title_freq_list, res_titles, k, 1)
    return res_titles


def print_titles(res_titles, count=10):
    global index_path
    global out_file

    ctr_val = 0
    for k, v in res_titles.items():
        if ctr_val == count:
            break
        title_id, batch_num = k.split("_")
        index_val = int(int(title_id) / 100000)
        fp = open(index_path + "title_" + str(batch_num) + ".txt", "r")
        res = get_element("title_dict_fin_" + str(index_val) + ".txt", title_id)
        if res is not None:
            title_dict = extract_title_info(res)
            seek_val = title_dict[title_id][int(batch_num)][0]
            fp.seek(seek_val)
            ans_title = fp.readline()
            out_file.write(title_id + ", " + ans_title)
        ctr_val += 1
        fp.close()


def get_index(ele):
    fp = open(index_path + dict_path + "word_secondary.txt", "r")
    line = fp.readline()
    tokens = line.split(" ")
    for indx, token in enumerate(tokens):
        if ele < token:
            return indx - 1
    return -1


def search(search_str):
    global index_path
    search_str = pre_process_text(search_str)
    res_titles = dict()
    for ele in search_str:
        index_val = get_index(ele)
        if index_val != -1:
            res = get_element("word_dict_fin_" + str(index_val) + ".txt", ele)
            if res is not None:
                res_titles = get_result(res, ele, res_titles)
    res_titles = sort_dict(res_titles)
    print_titles(res_titles)


def get_field_query(search_query):
    field_query = dict()
    search_query = search_query.split(":")
    i = 0
    while i < len(search_query):
        if i == 0:
            if search_query[i] == 'l':
                field_query['e'] = search_query[i + 1][:-1]
            else:
                field_query[search_query[i]] = search_query[i + 1][:-1]
            i += 2
        else:
            if search_query[i - 1][-1] == 'l':
                field_query['e'] = search_query[i][:-1]
            else:
                field_query[search_query[i - 1][-1]] = search_query[i][:-1]
            i += 1
    return field_query


def field_search(search_query):
    field_query = get_field_query(search_query)
    fin_res_titles = dict()
    title_covered = set()
    title_mod = False
    for k, v in field_query.items():
        search_str = pre_process_text(v)
        res_titles = dict()
        for ele in search_str:
            index_val = get_index(ele)
            if index_val != -1:
                res = get_element("word_dict_fin_" + str(index_val) + ".txt", ele)
                if res is not None:
                    res_titles = get_result(res, ele, res_titles, field=k)
                    fin_res_titles = get_result(res, ele, fin_res_titles, field=k)
                    if title_mod:
                        title_covered = title_covered.intersection(set(res_titles.keys()))
                    else:
                        title_covered = set(res_titles.keys())
                        title_mod = True

    intersect_dict = dict()
    for ele in title_covered:
        intersect_dict[ele] = res_titles[ele]
    intersect_dict = sort_dict(intersect_dict)
    print_titles(intersect_dict)
    if len(intersect_dict) < 10:
        fin_res_titles = sort_dict(fin_res_titles)
        print_titles(fin_res_titles, 10 - len(intersect_dict))
    # print(len(intersect_dict))


if __name__ == "__main__":  # main
    # search_query = input("Enter search query\n")

    out_file = open("queries_op.txt", "w")
    in_path = sys.argv[1]
    fp = open(in_path, "r")
    search_query = fp.readline()
    while search_query:
        start = timeit.default_timer()
        if len(search_query.split(":")) > 1:
            field_search(search_query)
        else:
            search(search_query)
        start1 = timeit.default_timer()

        out_file.write(str(start1 - start) + "\n\n")

        search_query = fp.readline()

    out_file.close()
    fp.close()
