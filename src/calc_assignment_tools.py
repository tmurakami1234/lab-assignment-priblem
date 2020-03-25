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


def HNG(data):
    pass


"""
    def square_sum_of_dissatisfaction(self):
        '''
        不満の最小自乗和
        '''
        self.set_W_and_A(self.S_labels, self.T_labels)
        _sum = 0.
        for s in range(len(self.S_labels)):
            for t in range(len(self.T_labels)):
                _sum += self.x[s, t]*(100.-self.A[s, t]*self.W[s, t])**2
        return _sum


    def assignment2x(self):
        '''
        assignmentをxに変換する関数.
        '''
        self.x = np.zeros((len(self.S_labels), len(self.T_labels)), int)
        for teacher in self.assignment.keys():
            for student in self.assignment[teacher]:
                s = self.S_labels.index(student)
                t = self.T_labels.index(teacher)
                self.x[s, t] = 1

    def x2assignment(self):
        '''
        xをassignmentに変換する関数.
        '''
        self.assignment = {teacher: [] for teacher in self.T_labels}
        for s, student in enumerate(self.S_labels):
            for t, teacher in enumerate(self.T_labels):
                if self.x[s, t] == 1:
                    self.assignment[teacher].append(student)

"""
