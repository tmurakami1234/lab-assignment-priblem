import numpy as np
from munkres import Munkres


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
    pass


def HNG(data):
    pass


"""

    class LAP:
    '''
    研究室配属問題を解くためのクラス.
    '''

    def __init__(self, method='DA',
                 min_rank=1, max_rank=10, unranked=20,
                 max_wishness=100., min_wishness=50.,
                 max_acceptability=1., min_acceptability=0.):
        # 定数
        self.method = method
        self.dict_teachers = None
        self.dict_students = None
        self.S_labels = None
        self.T_labels = None
        self.effective_T_labels = None
        self.min_rank = min_rank  # 希望順位の最小値(最高希望順位)
        self.max_rank = max_rank  # 希望順位の最大値(最低希望順位)
        self.unranked = unranked  # 希望外の値
        self.min_preference = 1  # 選好順位の最小値(最低選好順位)
        self.max_preference = None  # 選好順位の最大値(最高選好順位)
        self.max_wishness = max_wishness
        self.min_wishness = min_wishness
        self.max_acceptability = max_acceptability
        self.min_acceptability = min_acceptability
        # 変数
        self.assignment = None
        self.x = None
        self.W = None
        self.A = None
        self.U = None
        self.result = None

    def prep(self):
        '''
        前処理.
        '''
        self.S_labels = list(self.dict_students.keys())
        self.T_labels = list(self.dict_teachers.keys())
        self.effective_T_labels = []
        for teacher in self.T_labels:
            capacity = int(self.dict_teachers[teacher]['capacity'])
            for _ in range(capacity):
                self.effective_T_labels.append(teacher)
        self.max_preference = len(self.S_labels)
        self.U = np.array([int(self.dict_teachers[teacher]['capacity'])
                           for teacher in self.T_labels])
        self.reset_x_and_assignment()

    def reset_x_and_assignment(self):
        self.assignment = {teacher: [] for teacher in self.T_labels}
        self.x = np.zeros((len(self.S_labels), len(self.T_labels)), int)

    def set_W_and_A(self, S_labels, T_labels):
        '''
        WとAに要素を代入する関数.
        '''
        self.W = np.zeros((len(S_labels), len(T_labels)), float)
        self.A = np.zeros((len(S_labels), len(T_labels)), float)
        for s, student in enumerate(S_labels):
            dict_rank = {teacher: int(rank) for rank, teacher
                         in self.dict_students[student].items()}
            for t, teacher in enumerate(T_labels):
                if teacher in dict_rank.keys():
                    rank = int(dict_rank[teacher])
                else:
                    rank = self.unranked
                self.W[s, t] = self.wishness(rank)
                preference = self.dict_teachers[teacher][
                    'preference'][student]
                self.A[s, t] = self.acceptability(preference)

    def wishness(self, rank):
        '''
        rankからwishnessを計算する関数.
        wishnessはrankの単調減少関数.
        '''
        srope = (self.max_wishness-self.min_wishness) / \
            (self.min_rank - self.unranked)
        intercept = self.max_wishness-srope*self.min_rank
        return srope*rank+intercept

    def acceptability(self, preference):
        '''
        preferenceからacceptabilityを計算する関数.
        acceptabilityはpreferenceの単調増加関数.
        '''
        srope = ((self.max_acceptability-self.min_acceptability)
                 / (self.max_preference-self.min_preference))
        intercept = self.max_acceptability-srope*self.max_preference
        return srope*preference+intercept

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

    def check_capacity(self):
        '''
        x, Uを用いて定員を超過した研究室があるか判定する.
        '''
        for t in range(len(self.T_labels)):
            capacity = self.U[t]
            if sum(self.x[:, t]) > capacity:
                raise RuntimeError('定員を超過した研究室が存在します.')

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


    def MNK(self, verbose=False):
        '''
        munkresモジュールを用いて割当問題の最適解を1つだけ導く.
        '''
        self.reset_x_and_assignment()
        self.set_W_and_A(self.S_labels, self.effective_T_labels)
        M = (100.-self.W*self.A)**2
        sol = Munkres().compute(M)
        for s, t in sol:
            teacher = self.effective_T_labels[t]
            t = self.T_labels.index(teacher)
            self.x[s, t] = 1

        self.check_capacity()
        self.x2assignment()
        ssd = self.square_sum_of_dissatisfaction()

        self.result = {}
        self.result['method'] = self.method
        self.result['assignment'] = self.assignment
        self.result['SSD'] = ssd

        if verbose:
            self.print_result()

"""
