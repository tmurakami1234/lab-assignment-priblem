import numpy as np
from munkres import Munkres
from pprint import pprint


def DA(data):
    '''
    deferred acceptance algorithmにより配属を決定する関数.
    配属が決まらなかった学生はassignment['未配属']に格納される.
    '''
    assignment = {t: [] for t in list(data['teachers'].keys())}
    unassigned = list(data['students'].keys())
    limit = len(data['students'][list(data['students'].keys())[0]]['choice'])
    # 第1志望から順に未配属の学生を配属していく.
    for i in range(1, limit+1):
        for s in unassigned:
            choice = data['students'][s]['choice'].items()
            for t, j in choice:
                if i == j:
                    break
            assignment[t].append(s)
        # 教員の選好順位を元に配属者数を定員に収める.
        unassigned = []
        for t in data['teachers'].keys():
            c = data['teachers'][t]['capacity']
            if len(assignment[t]) > c:
                applicants = sorted(
                    [
                        (s, data['teachers'][t]['preference'][s])
                        for s in assignment[t]
                    ],
                    key=lambda x: x[1]
                )
                assignment[t] = [x[0] for x in applicants[:c]]
                # 定員からあぶれた生徒はunassignedに格納される.
                unassigned += [x[0] for x in applicants[c:]]

    if len(unassigned) != 0:
        assignment['未配属'] = unassigned

    return assignment


def MNK(data):
    '''
    munkresモジュールを用いて割当問題の最適解を1つだけ導く関数.
    '''
    assignment = {t: [] for t in data['teachers'].keys()}
    vars_dict = _get_vars_dict(data)
    M = (100.-vars_dict['W']*vars_dict['A'])**2
    sol = Munkres().compute(M)
    for i, j in sol:
        s = vars_dict['S'][i]
        t = vars_dict['U'][j]
        assignment[t].append(s)

    _breakup(assignment, data)
    return assignment


def HNG(data):
    '''
    ハンガリー法を用いて割当問題の最適解を全て導く関数.
    ハンガリー法はhungarian関数で実装されている.
    '''
    assignments = []
    vars_dict = _get_vars_dict(data)
    M = (100.-vars_dict['W']*vars_dict['A'])**2
    sols = Hungarian(M).compute()
    for sol in sols:
        assignment = {t: [] for t in data['teachers'].keys()}
        for i, j in sol:
            s = vars_dict['S'][i]
            t = vars_dict['U'][j]
            assignment[t].append(s)

        _breakup(assignment, data)
        if not _overlapping(assignment, assignments):
            assignments.append(assignment)

    return assignments[0]


def square_sum_of_dissatisfaction(assignment, data):
    '''
    不満の最小自乗和を計算する関数
    '''
    vars_dict = _get_vars_dict(data)
    _sum = 0.
    for i, s in enumerate(vars_dict['S']):
        for j, t in enumerate(vars_dict['U']):
            x = 1 if s in assignment[t] else 0
            _sum += x*(100.-vars_dict['W'][i, j]*vars_dict['A'][i, j])**2
    return _sum


def _overlapping(assignment, assignments):
    '''
    assignmentがassignmentsに含まれる場合True, そうでなければFalseを返す関数.
    '''
    overlapping = False
    for a in assignments:
        overlapping = True
        for t, slist in a.items():
            if set(assignment[t]) != set(slist):
                overlapping = False
                break
        if overlapping:
            return overlapping
    return overlapping


def _breakup(assignment, data):
    '''
    教員に配属された学生数が定員を超えている場合, その学生を未配属にする関数.
    '''
    unassigned = []
    for t, slist in assignment.items():
        if len(slist) > data['teachers'][t]['capacity']:
            unassigned += slist
            assignment[t] = []

    if len(unassigned) != 0:
        assignment['未配属'] = unassigned


def _get_vars_dict(data):
    '''
    dataを計算しやすい形式に変換する関数.
    '''
    vars_dict = {}
    vars_dict['S'] = list(data['students'].keys())
    vars_dict['T'] = list(data['teachers'].keys())
    vars_dict['U'] = sum(
        [
            [t for _ in range(data['teachers'][t]['capacity'])]
            for t in data['teachers'].keys()
        ],
        []
    )
    vars_dict['W'] = _calc_W(data, vars_dict['S'], vars_dict['U'])
    vars_dict['A'] = _calc_A(data, vars_dict['S'], vars_dict['U'])
    return vars_dict


def _calc_W(data, S, T, limit=None, unchoice=20):
    '''
    学生sが教員tを志望する度合いW_stを元に持つ行列Wを計算して返す関数.
    limitはWの元の上限と下限を定めるリストである.
    '''
    _limit = [100., 50.]
    li = list(data['students'][S[0]]['choice'].values())
    if max(li) >= unchoice:
        msg = 'Value of argument unchoice must be greater than max choice ranking number.'
        raise RuntimeError(msg)
    ilimit = [min(li), unchoice]
    msg = 'Argument limit must be list of which length is 2.'
    if limit is None:
        limit = _limit
    elif type(limit) is not list:
        raise RuntimeError(msg)
    elif len(limit) != 2:
        raise RuntimeError(msg)
    olimit = limit
    W = np.zeros((len(S), len(T)), float)
    for i, s in enumerate(S):
        for j, t in enumerate(T):
            if t in data['students'][s]['choice'].keys():
                k = int(data['students'][s]['choice'][t])
            else:
                k = unchoice
            W[i, j] = _calc_w(k, ilimit, olimit)
    return W


def _calc_w(_in, ilimit, olimit):
    '''
    志望順位_inからW_stを計算する関数.
    W_stは志望順位の単調減少関数.
    '''
    srope = (max(olimit)-min(olimit))/(min(ilimit)-max(ilimit))
    intercept = max(olimit)-srope*min(ilimit)
    return srope*_in+intercept


def _calc_A(data, S, T, limit=None):
    '''
    教員tが学生sを選好する度合いA_stを元に持つ行列Aを計算して返す関数.
    limitはAの元の上限と下限を定めるリストである.
    '''
    _limit = [1., 0.]
    li = list(data['teachers'][T[0]]['preference'].values())
    ilimit = [min(li), max(li)]
    msg = 'Argument limit must be list of which length is 2.'
    if limit is None:
        limit = _limit
    elif type(limit) is not list:
        raise RuntimeError(msg)
    elif len(limit) != 2:
        raise RuntimeError(msg)
    olimit = limit
    A = np.zeros((len(S), len(T)), float)
    for i, s in enumerate(S):
        for j, t in enumerate(T):
            k = data['teachers'][t]['preference'][s]
            A[i, j] = _calc_a(k, ilimit, olimit)
    return A


def _calc_a(_in, ilimit, olimit):
    '''
    選好順位_inからA_stを計算する関数.
    A_stは選好順位の単調減少関数.
    '''
    srope = (max(olimit)-min(olimit))/(min(ilimit)-max(ilimit))
    intercept = max(olimit)-srope*min(ilimit)
    return srope*_in+intercept


class Hungarian:
    '''
    hungarian algorithm.
    '''

    def __init__(self, matrix):
        self.matrix = np.array(matrix)
        nrow, ncol = matrix.shape
        if nrow != ncol:
            raise RuntimeError('正方行列を入力して下さい.')
        self.N = nrow
        self.binary_matrix = np.zeros((self.N, self.N, 2), int)

    def step1(self):
        '''
        各行の要素からその行の最小値を引く.
        各列の要素からその列の最小値を引く.
        '''
        for i in range(self.N):
            self.matrix[i, :] -= np.min(self.matrix[i, :])
        for j in range(self.N):
            self.matrix[:, j] -= np.min(self.matrix[:, j])

    def step2(self):
        '''
        割当が存在すれば全ての割当を出力する.
        '''
        roots = {'0': []}
        for i in range(self.N):
            temp = []
            for j in range(self.N):
                if self.matrix[i, j] == 0:
                    temp.append(j)
            keys = list(roots.keys())
            for key in keys:
                for n, j in enumerate(temp):
                    if j not in roots[key]:
                        new_key = f'{key}{n}'
                        roots[new_key] = list(roots[key])
                        roots[new_key].append(j)
            for key in keys:
                roots.pop(key)
        sols = []
        for key in roots.keys():
            if len(roots[key]) == self.N:
                sol = [(i, j) for i, j in enumerate(roots[key])]
                sols.append(sol)
        return sols

    def step3(self):
        '''
        値が0である要素を出来るだけ少ない数の線で隠す.
        '''
        for i in range(self.N):
            for j in range(self.N):
                self.binary_matrix[i, j, 0] = 0
                self.binary_matrix[i, j, 1] = 0
        for i in range(self.N):
            for j in range(self.N):
                if self.matrix[i, j] == 0:
                    self.binary_matrix[i, j, 0] = 1

        max_val = {'row': {'ind': 0, 'val': 0}, 'col': {'ind': 0, 'val': 0}}
        while True:
            _next = 'row' if np.random.rand() < 0.5 else 'col'
            max_val['row']['val'] = 0
            max_val['col']['val'] = 0
            for i in range(self.N):
                val = np.sum(self.binary_matrix[i, :, 0])
                if val > max_val['row']['val']:
                    max_val['row']['val'] = val
                    max_val['row']['ind'] = i
            for j in range(self.N):
                val = np.sum(self.binary_matrix[:, j, 0])
                if val > max_val['col']['val']:
                    max_val['col']['val'] = val
                    max_val['col']['ind'] = j

            if max_val['row']['val'] == 0 and max_val['col']['val'] == 0:
                break

            if ((max_val['row']['val'] > max_val['col']['val']) or
                (max_val['row']['val'] == max_val['col']['val']
                 and _next == 'row')):
                i = max_val['row']['ind']
                for j in range(self.N):
                    self.binary_matrix[i, j, 0] = 0
                    self.binary_matrix[i, j, 1] += 1
            else:
                j = max_val['col']['ind']
                for i in range(self.N):
                    self.binary_matrix[i, j, 0] = 0
                    self.binary_matrix[i, j, 1] += 1

    def step4(self):
        '''
        線で隠れていない部分から最小値min_valを求める.
        線で隠れていない要素からmin_valを引き,
        2本の線で隠されている要素にmin_valを足す.
        '''
        min_val = np.max(self.matrix)
        for i in range(self.N):
            for j in range(self.N):
                if (self.binary_matrix[i, j, 1] == 0 and
                        min_val > self.matrix[i, j]):
                    min_val = self.matrix[i, j]

        for i in range(self.N):
            for j in range(self.N):
                if self.binary_matrix[i, j, 1] == 0:
                    self.matrix[i, j] -= min_val
                elif self.binary_matrix[i, j, 1] == 2:
                    self.matrix[i, j] += min_val

    def print_bm(self, channel):
        '''
        binary_matrixを標準出力する関数.
        channel=0でmatrixの要素の値が0である箇所を1とした行列を出力し,
        channel=1でその要素が何本の線で覆われたかを表す行列を出力する.
        '''
        text = f'BINARY_MATRIX_{channel}\n'
        for i in range(self.N):
            for j in range(self.N):
                text += f'{self.binary_matrix[i,j,channel]:d} '
            text += '\n'
        print(text[:-1])

    def print_m(self):
        '''
        matrixを標準出力する関数.
        '''
        text = f'MATRIX\n'
        for i in range(self.N):
            for j in range(self.N):
                text += f'{self.matrix[i,j]:8.3f} '
            text += '\n'
        print(text[:-1])

    def compute(self):
        '''
        割当を計算する関数.
        '''
        self.step1()
        while True:
            sols = self.step2()
            if len(sols) != 0:
                return sols
            self.step3()
            self.step4()
