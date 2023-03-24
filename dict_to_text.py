import pickle
import timeit
import os
import collections

index_path = "index/"
dir_name = "final"


def create_index_dir():
    global index_path
    global dir_name
    dir_path = os.getcwd()
    if not os.path.isdir(dir_path + "/" + index_path + dir_name):
        os.mkdir(dir_path + "/" + index_path + dir_name)


def load_dict(path):
    infile = open(path, 'rb')
    new_dict = pickle.load(infile)
    infile.close()
    new_dict = collections.OrderedDict(sorted(new_dict.items()))
    return new_dict


# def get_batch_count(div_val):
#     dir_list = os.listdir(index_path)
#     return int(len(dir_list) / div_val)

def get_batch_count(file_name):
    dir_list = os.listdir(index_path)
    ctr_val = 0
    for ele in dir_list:
        if ele.startswith(file_name):
            ctr_val += 1
    return ctr_val


def dict_to_text(file_name, file_num, file_type="dict"):
    global index_path
    start = timeit.default_timer()
    final_path = index_path + dir_name + "/"
    new_dict = load_dict(index_path + file_name)
    fp1 = open(final_path + file_name + ".txt", "w")
    arr_map = {'b': 0, 't': 1, 'e': 2, 'c': 3, 'i': 4, 'r': 5}
    for k, v in new_dict.items():
        if file_type == "dict":
            str_val = k + "-" + str(file_num) + ":"
            inner_dict = v
            temp_val = ['n', 'n', 'n', 'n', 'n', 'n']
            for in_k, in_v in inner_dict.items():
                temp_val[arr_map[in_k]] = in_v
            for indx, ele in enumerate(temp_val):
                if indx != len(temp_val) - 1:
                    str_val += str(ele) + " "
                else:
                    str_val += str(ele)
        else:
            str_val = str(k) + "-" + str(file_num) + ":"
            for indx, ele in enumerate(v):
                if indx != len(v) - 1:
                    str_val += str(ele) + " "
                else:
                    str_val += str(ele)
        str_val += "\n"
        fp1.write(str_val)
    fp1.close()
    start1 = timeit.default_timer()
    # print("Conversion Time: {0} \t Index: {1}".format(start1 - start, file_num))


def convert_all(file_name, file_type):
    global index_path
    create_index_dir()
    batches = get_batch_count(file_name)
    for i in range(0, batches):
        fin_file_name = file_name + str(i)
        dict_to_text(fin_file_name, i, file_type)
        os.remove(index_path + fin_file_name)


# convert_all("word_dict_", "dict")
# convert_all("title_dict_", "list")
