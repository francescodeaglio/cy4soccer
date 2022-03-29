

def isNet(array):
    vect = [0]*len(array)
    return pass_net_check(1, len(array),vect, array)


def pass_net_check(i, n, vect, check):
    if i == 1:
        vect[i - 1] = "A"
        return pass_net_check(2, n, vect, check)
    elif i == 2:
        vect[i - 1] = "B"
        return pass_net_check(3, n, vect, check)
    elif i == n + 1:
        if vect == check:
            return True
        else:
            return False
    else:
        for l in distinct_letters(vect, i - 2):

            vect[i - 1] = l
            a = pass_net_check(i + 1, n, vect, check)
            if a:
                return a
        vect[i - 1] = first_new_letter(vect, i - 1)
        a = pass_net_check(i + 1, n, vect, check)
        if a:
            return a
def first_new_letter(vect,end):
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "L", "M"]
    max_letter = max(vect[:end])
    return letters[letters.index(max_letter)+1]

def distinct_letters(vect, end):
    el = set(vect[:end])
    el.discard(vect[end])
    return list(el)

def read(path):
    '''
    Read content of a file
    '''
    with open(path, 'r') as f:
        return f.read()


