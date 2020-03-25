import argparse
import json
import numpy as np
from pathlib import Path
from calc_assignment_tools import (
    DA,
    MNK,
    HNG
)

# グローバル変数
method = ['DA', 'MNK', 'HNG']


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
        研究室配属を計算するスクリプト.
        '''
    )
    p.add_argument(
        '--input',
        type=is_file,
        required=True,
        metavar='FILE',
        help='''
        入力ファイルを指定して下さい.
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
        '--method',
        type=str,
        choices=method,
        default=method[0],
        metavar='STRING',
        help='''
        配属の計算に用いるアルゴリズムを指定して下さい.
        '''
    )
    p.add_argument(
        '--verbose',
        action='store_true',
        help='''
        配属結果を標準出力します.
        '''
    )
    args = p.parse_args()
    # 引数の前処理.
    args.input = Path(args.input)
    args.output = Path(args.output)

    return args


def load(path):
    '''
    jsonlファイルからデータを読み込む.
    '''
    with path.open('r') as f:
        text = f.read()
        data = json.loads(text)
    return data


def save(assignment, path, name):
    '''
    配属結果をjsonファイルで出力する.
    '''
    with (path/name).open('w') as f:
        text = json.dumps(
            assignment, sort_keys=True, ensure_ascii=False, indent=2
        )
        f.write(text)
    print(f'{(path/name).resolve()} saved.')


def print_assignment(assignment, data):
    msg = '{\n'
    for t in data['teachers'].keys():
        msg += f'  \"{t}\" (capacity: {data["teachers"][t]["capacity"]}): [\n'
        for s in assignment[t]:
            msg += f'    \"{s}\" (choice: {data["students"][s]["choice"][t]}),\n'
        if len(assignment[t]) == 0:
            msg = msg [:-1]
        else:
            msg = msg [:-2]
            msg += '\n  '
        msg += '],\n'
    if '未配属' in assignment.keys():
        msg += '  \"未配属\": [\n'
        for s in assignment['未配属']:
            msg += f'    \"{s}\",\n'
        msg = msg [:-2]
        msg += '\n  ],\n'
    msg = msg [:-2]
    msg += '\n}'
    print(msg)


if __name__ == '__main__':
    # 引数処理.
    args = get_arguments()
    # データを読み込む.
    data = load(args.input)
    # 配属を計算.
    if args.method == method[0]:
        assignment = DA(data)
    elif args.method == method[1]:
        assignment = MNK(data)
    else:
        pass
    if args.verbose:
        print_assignment(assignment, data)
    # 配属結果を出力.
    name = f'assignment_{args.method}_{args.input.stem}.json'
    name_list = [p.name for p in args.output.glob('*')]
    i = 1
    while name in name_list:
        name = f'assignment_{args.method}_{args.input.stem}({i}).json'
        i += 1
    save(assignment, args.output, name)
