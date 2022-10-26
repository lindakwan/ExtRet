import random

def shuffle_data(in_filename, out_filename):
    lines = open(in_filename, encoding='utf-8').readlines()
    random.shuffle(lines)
    open(out_filename, 'w', encoding='utf-8').writelines(lines)

def take_subset(in_filename, out_filename, start, end):
    in_file  = open(in_filename , "r", encoding='utf-8')
    out_file = open(out_filename, "w", encoding='utf-8')

    for i in range(start, end):
        line = in_file.readline()
        out_file.write(line)

    in_file.close()
    out_file.close()

def train_valid_test_split(in_filename, train_filename, valid_filename, test_filename, train_p=0.8, valid_p=0.1):

    file_length = sum(1 for _ in open(in_filename, "r", encoding='utf-8'))
    print("File length:", file_length)
    train_size = int(file_length * train_p)
    valid_size = int(file_length * valid_p)
    test_size = file_length - train_size - valid_size

    in_file    = open(in_filename,    "r", encoding='utf-8')
    train_file = open(train_filename, "w", encoding='utf-8')
    valid_file = open(valid_filename, "w", encoding='utf-8')
    test_file  = open(test_filename,  "w", encoding='utf-8')

    for _ in range(train_size):
        line = in_file.readline()
        train_file.write(line)

    for _ in range(valid_size):
        line = in_file.readline()
        valid_file.write(line)

    for _ in range(test_size):
        line = in_file.readline()
        test_file.write(line)

    in_file.close()
    train_file.close()
    valid_file.close()
    test_file.close()
    
def train_test_split(in_filename, train_filename, test_filename, train_p=0.8):
    file_length = sum(1 for _ in open(in_filename, "r", encoding='utf-8'))
    print("File length:", file_length)
    train_size = int(file_length * train_p)
    test_size = file_length - train_size

    in_file    = open(in_filename,    "r", encoding='utf-8')
    train_file = open(train_filename, "w", encoding='utf-8')
    test_file  = open(test_filename,  "w", encoding='utf-8')

    for _ in range(train_size):
        line = in_file.readline()
        train_file.write(line)

    for _ in range(test_size):
        line = in_file.readline()
        test_file.write(line)

    in_file.close()
    train_file.close()
    test_file.close()