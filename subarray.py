from collections import Counter
from typing import List


class Solution:
    def __init__(self):
        self.mod_array = []

    def modify_array(self, arr) -> List[int]:
        for elem in arr:
            if type(elem) == list:
                self.modify_array(elem)
            else:
                self.mod_array.append(elem)
        return self.mod_array

    def count_elements(self, arr):
        res = []
        mod_arr = self.modify_array(arr)
        elms_counts = Counter(mod_arr)
        most_com = elms_counts.most_common()
        max_num = most_com[0][1]
        for elem in most_com:
            if elem[1] == max_num:
                res.append(elem[0])
        res.sort()
        return " ".join(map(str, res))


print(Solution().count_elements([0, 10, 2, 5, -999999999]))
