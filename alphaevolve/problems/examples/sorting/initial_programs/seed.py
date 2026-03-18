def sort_list(lst):
    lst = list(lst)
    for i in range(len(lst)):
        for j in range(len(lst) - 1 - i):
            if lst[j] > lst[j+1]: lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst
