import os
import timeit

index_path = "index/final/"

token_count = 0


def split_file(file_name, threshold, res_file_name):
    global token_count
    fp = open(index_path + file_name + ".txt", "r")
    line = fp.readline()
    line_ctr = 0
    file_count = 0
    word_list = []
    while line:
        fp1 = open(index_path + res_file_name + "_" + str(file_count) + ".txt", "w")
        word_list.append(line.split("-")[0])
        while line_ctr < threshold:
            fp1.write(line)
            line_ctr += 1
            line = fp.readline()
        if file_name == "word_dict_0":
            token_count += line_ctr
        line_ctr = 0
        fp1.close()
        file_count += 1
    fp.close()
    os.remove(index_path + file_name + ".txt")
    return word_list


def store_list(file_name, file_list):
    fp = open(index_path + file_name + ".txt", "w")
    for ele in file_list:
        fp.write(ele + " ")
    fp.close()


# file_list = split_file("word_dict_0", 1000000, "word_dict_fin")
# store_list("word_secondary", file_list)
# file_list = split_file("title_dict_0", 100000, "title_dict_fin")
