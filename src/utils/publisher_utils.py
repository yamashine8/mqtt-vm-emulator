import random

CHARS = ["A", "X", "Q", "H", "F"]

def generate_names(names_num):
    names_list = [generate_name() for _ in range(names_num)]
    return names_list

def generate_name():
    name = ""
    for i in range(5):
        if i % 2 == 0:
            name = name + random.choice(CHARS)
        else:
            name = name + str(random.randint(100, 200))
    return name
