import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from pprint import pprint


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
        xlsxやxls, csv, tsvファイルを変換して, main.pyの入力に指定可能なjsonファイルを出力するスクリプト.
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
    args = p.parse_args()
    # 引数の前処理.
    args.input = Path(args.input)
    args.output = Path(args.output)

    return args


def load(path):
    '''
    入力ファイルを読み込み, pandas.core.frame.DataFrameを返す関数.
    '''
    if path.suffix in ['.xls', '.xlsx']:
        df = pd.read_excel(path)
    elif path.suffix == '.csv':
        df = pd.read_csv(path)
    elif path.suffix == '.tsv':
        df = pd.read_csv(path, sep='\t')
    return df


def switch(bln, pvalue, cvalue):
    if pvalue is np.nan and cvalue is not np.nan:
        return True
    elif pvalue is not np.nan and cvalue is np.nan:
        return False
    else:
        return bln


def convert(df):
    '''
    pandas.core.frame.DataFrameをmain.pyの入力に使用可能なdictに変換する関数.
    '''
    nrow, ncol = df.shape
    values = df.values

    # 生徒名と教員名を取得.
    bln, subli, li = False, [], []
    for i in range(1, nrow):
        bln = switch(bln, values[i-1, 0], values[i, 0])
        if bln:
            subli.append(values[i, 0])
        if (bln and i == nrow-1) or (not bln and len(subli) != 0):
            li.append(subli)
            subli = []

    S, T = li
    ns, nt = len(S), len(T)
    data = {
        'students': {s: {'choice': {}} for s in S},
        'teachers': {t: {'preference': {}} for t in T}
    }

    # 選好順位 (preference) の数が生徒数と一致するか確認.
    if values[ns+3, 2] != 'preference':
        raise RuntimeError('item \"preference\" is not found.')
    bln, counter = False, 0
    for j in range(2, ncol):
        bln = switch(bln, values[8, j-1], values[8, j])
        if bln:
            counter += 1
        if not bln and counter != 0:
            break
    if counter != ns:
        msg = (
            f'The number of ranks of preference ranking must be equal to'
            + ' The number of students'
        )
        raise RuntimeError(msg)

    # 選好順位 (preference) と教員が受け持てる学生の定員数 (capacity) を取得.
    if values[ns+3, 1] != 'capacity':
        raise RuntimeError('item \"capacity\" is not found.')
    for i, t in enumerate(T):
        data['teachers'][t]['capacity'] = values[i+ns+5, 1]
        for j in range(ns):
            s = values[i+ns+5, 2+j]
            data['teachers'][t]['preference'][s] = j+1

    # 志望順位 (choice) の数 (limit) を取得.
    if values[0, 1] != 'choice':
        raise RuntimeError('item \"choice\" is not found.')
    bln, limit = False, 0
    for j in range(1, ncol):
        bln = switch(bln, values[1, j-1], values[1, j])
        if bln:
            limit += 1
        if not bln and limit != 0:
            break

    # 志望順位 (choice) を取得.
    for i, s in enumerate(S):
        for j in range(limit):
            t = values[i+2, j+1]
            data['students'][s]['choice'][t] = j+1

    return data


if __name__ == '__main__':
    args = get_arguments()
    # 入力の読み込み.
    df = load(args.input)
    # 変換
    data = convert(df)
    # jsonファイルを出力.
    name = f'{args.input.stem}.json'
    name_list = [p.name for p in args.output.glob('*')]
    i = 1
    while name in name_list:
        name = f'{args.input.stem}({i}).json'
        i += 1
    with (args.output/name).open(mode='w') as f:
        text = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2)
        f.write(text)
