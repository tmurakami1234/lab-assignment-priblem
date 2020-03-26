import argparse
import json
import numpy as np
from pathlib import Path

# グローバル変数
opt = ['random', 'separate']


def is_file(string):
    '''
    引数がファイルであるか判定する関数. get_arguments関数で用いている.
    '''
    if not Path(string).is_file():
        raise argparse.ArgumentTypeError(f'{string} is not file.')
    return string


def is_dir(string):
    '''
    引数がディレクトリであるか判定する関数. get_arguments関数で用いている.
    '''
    if not Path(string).is_dir():
        raise argparse.ArgumentTypeError(f'{string} is not directory.')
    return string


def get_arguments():
    '''
    引数処理を行う関数.
    '''
    fc = argparse.ArgumentDefaultsHelpFormatter
    p = argparse.ArgumentParser(
        formatter_class=fc,
        description='''
        研究室配属のデモデータを作製するスクリプト.
        '''
    )
    p.add_argument(
        '--output',
        type=is_dir,
        default='./',
        metavar='DIR',
        help='''
        出力ディレクトリを指定して下さい.
        '''
    )
    p.add_argument(
        '--ns',
        type=int,
        default=20,
        metavar='INT',
        help='''
        生徒数を指定して下さい.
        '''
    )
    p.add_argument(
        '--nt',
        type=int,
        default=15,
        metavar='INT',
        help='''
        教員数を指定して下さい.
        '''
    )
    p.add_argument(
        '--limit',
        type=int,
        default=10,
        metavar='INT',
        help='''
        志望順位の数を指定して下さい.
        '''
    )
    p.add_argument(
        '--opt',
        type=str,
        choices=opt,
        default=opt[0],
        help='''
        デモデータ作製時のオプションを指定して下さい.
        '''
    )
    args = p.parse_args()
    # 引数の前処理.
    args.output = Path(args.output)

    return args


def random_choice(data, limit=None):
    '''
    各教員に対する生徒の志望順位をランダムに設定する関数.
    '''
    tea = list(data['teachers'].keys())
    if limit is None or limit > len(tea):
        limit = len(tea)
    for s in data['students'].keys():
        np.random.shuffle(tea)
        for i, t in enumerate(tea[:limit]):
            data['students'][s]['choice'][t] = i+1


def separate_choice(data, limit=None):
    '''
    全ての生徒が第1志望の教員に配属されるように, 各教員に対する生徒の志望順位を設定する関数.
    '''
    tea = set(data['teachers'].keys())
    if limit is None or limit > len(tea):
        limit = len(tea)
    capacity = {t: data['teachers'][t]['capacity'] for t in tea}
    # 第1志望の設定.
    for s in data['students'].keys():
        p = np.array(list(capacity.values()))
        t = np.random.choice(list(capacity.keys()), p=p/float(p.sum()))
        data['students'][s]['choice'][t] = 1
        capacity[t] -= 1
    # 第2志望以降の設定.
    for s in data['students'].keys():
        _tea = list(tea-set(data['students'][s]['choice'].keys()))
        np.random.shuffle(_tea)
        for i, t in enumerate(_tea[:limit-1]):
            data['students'][s]['choice'][t] = i+2


if __name__ == '__main__':
    args = get_arguments()
    data = {
        'students': {},
        'teachers': {}
    }
    # 学生の名前を設定.
    for i in range(args.ns):
        name = f'Student_{i}'
        data['students'][name] = {
            'choice': {}
        }
    # 教員の名前を設定.
    for i in range(args.nt):
        name = f'Teacher_{i}'
        data['teachers'][name] = {
            'capacity': 0,
            'preference': {}
        }
    # 教員が受け入れ可能な学生数を設定.
    tea = list(data['teachers'].keys())
    for i in range(args.ns):
        name = np.random.choice(tea)
        data['teachers'][name]['capacity'] += 1
    # 各学生に対する教員の選好順位を設定.
    stu = list(data['students'].keys())
    for t in tea:
        for i, s in enumerate(stu):
            data['teachers'][t]['preference'][s] = i+1
    # 各教員に対する生徒の志望順位を設定.
    if args.opt == opt[0]:
        random_choice(data, limit=args.limit)
    else:
        separate_choice(data, limit=args.limit)
    # デモデータを出力
    name = f'demodata_{args.opt}.json'
    name_list = [p.name for p in args.output.glob('*')]
    i = 1
    while name in name_list:
        name = f'demodata_{args.opt}({i}).json'
        i += 1
    with (args.output/name).open(mode='w') as f:
        text = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2)
        f.write(text)
