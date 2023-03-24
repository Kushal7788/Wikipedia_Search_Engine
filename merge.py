import os
import timeit

index_path = "index/final/"


def mergeFiles(file1, file2, res):
    f1 = open(index_path + file1 + ".txt", 'r')
    f2 = open(index_path + file2 + ".txt", 'r')
    output_file = open(index_path + "temp.txt", 'w')

    line1 = f1.readline()
    line2 = f2.readline()

    while line1 and line2:
        k1, v1 = line1.split("-")
        k2, v2 = line2.split("-")
        # k1 = int(k1)
        # k2 = int(k2)
        if k1 < k2:
            output_file.write(line1)
            line1 = f1.readline()
        elif k1 > k2:
            output_file.write(line2)
            line2 = f2.readline()
        else:
            v1 = v1.strip("\n")
            output_file.write(str(k1) + "-" + v1 + "," + v2)
            line1 = f1.readline()
            line2 = f2.readline()

    while line1:
        output_file.write(line1)
        line1 = f1.readline()

    while line2:
        output_file.write(line2)
        line2 = f2.readline()

    f1.close()
    f2.close()
    output_file.close()
    os.remove(index_path + file1 + ".txt")
    os.remove(index_path + file2 + ".txt")
    os.rename(index_path + "temp.txt", index_path + res + ".txt")

    # print("Files " + file1 + " and " + file2 + " merged into " + res)


def get_batch_count(file_name):
    dir_list = os.listdir(index_path)
    ctr_val = 0
    for ele in dir_list:
        if ele.startswith(file_name):
            ctr_val += 1
    return ctr_val


def merge_all(file_name):
    total_files = get_batch_count(file_name)
    while total_files != 1:
        ctr = 0
        loop_val = total_files
        if total_files % 2:
            loop_val = total_files - 1
        for i in range(0, loop_val, 2):
            mergeFiles(file_name + str(i),
                       file_name + str(i + 1), file_name + str(ctr))
            ctr += 1
        if total_files % 2:
            mergeFiles(file_name + str(0), file_name + str(total_files - 1), file_name + str(0))
        total_files = get_batch_count(file_name)


# merge_all("word_dict_")
# merge_all("title_dict_")
