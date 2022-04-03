

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
def getTeams():
    return {'Austria',
     'Belgium',
     'Croatia',
     'Czech_Republic',
     'Denmark',
     'England',
     'Finland',
     'France',
     'Germany',
     'Hungary',
     'Italy',
     'Netherlands',
     'MACEDONIA_REPUBLIC_OF',
     'Poland',
     'Portugal',
     'Russia',
     'Scotland',
     'Slovakia',
     'Spain',
     'Sweden',
     'Switzerland',
     'Turkey',
     'Ukraine',
     'Wales'}
def getGamesList():
        return {'Finland-Russia': 3788753,
 'Switzerland-Turkey': 3788765,
 'Belgium-Italy': 3795107,
 'England-Denmark': 3795221,
 'Italy-England': 3795506,
 'England-Germany': 3794688,
 'Sweden-Ukraine': 3794692,
 'Croatia-Spain': 3794686,
 'Belgium-Portugal': 3794687,
 'Italy-Austria': 3794685,
 'Germany-Hungary': 3788774,
 'Croatia-Scotland': 3788771,
 'Czech Republic-England': 3788772,
 'Finland-Belgium': 3788768,
 'Ukraine-Austria': 3788767,
 'Hungary-France': 3788763,
 'England-Scotland': 3788759,
 'Ukraine-North Macedonia': 3788758,
 'Denmark-Belgium': 3788757,
 'England-Croatia': 3788745,
 'Netherlands-Ukraine': 3788746,
 'France-Switzerland': 3794691,
 'Netherlands-Czech Republic': 3794690,
 'Wales-Denmark': 3794689,
 'Russia-Denmark': 3788769,
 'Sweden-Slovakia': 3788761,
 'Portugal-Germany': 3788764,
 'Italy-Wales': 3788766,
 'Italy-Switzerland': 3788754,
 'Turkey-Wales': 3788755,
 'Portugal-France': 3788773,
 'Spain-Poland': 3788762,
 'Croatia-Czech Republic': 3788760,
 'Austria-North Macedonia': 3788747,
 'Turkey-Italy': 3788741,
 'Italy-Spain': 3795220,
 'North Macedonia-Netherlands': 3788770,
 'Switzerland-Spain': 3795108,
 'Ukraine-England': 3795187,
 'Czech Republic-Denmark': 3795109,
 'Netherlands-Austria': 3788756,
 'Poland-Slovakia': 3788749,
 'Spain-Sweden': 3788750,
 'Scotland-Czech Republic': 3788748,
 'France-Germany': 3788751,
 'Hungary-Portugal': 3788752,
 'Denmark-Finland': 3788742,
 'Slovakia-Spain': 3788775,
 'Sweden-Poland': 3788776,
 'Belgium-Russia': 3788743,
 'Wales-Switzerland': 3788744}


