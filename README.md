# lab-assignment-problem
特研生の研究室配属を決定するスクリプト.

次のようにレポジトリをクローンして, main.pyにより研究室配属を計算し出力します.

```bash
$ # レポジトリをクローン.
$ git clone https://github.com/tmurakami1234/lab-assignment-problem.git
$ # python3.6以上でスクリプトを実行.
$ python lab-assignment-problem/src/main.py --input input.json --output output
$ # outputディレクトリ直下に配属結果が出力されます.
$ ls output
assignment_DA_input.json
```

main.pyのヘルプは以下のように確認出来ます.

```bash
$ python lab-assignment-problem/src/main.py --help
usage: main.py [-h] --input FILE [--output DIR] [--method STRING] [--verbose]

研究室配属を計算するスクリプト.

optional arguments:
  -h, --help       show this help message and exit
  --input FILE     入力ファイルを指定して下さい. (default: None)
  --output DIR     出力ディレクトリを指定して下さい. (default: ./)
  --method {DA,MNK,HNG}
                   配属の計算に用いるアルゴリズムを指定して下さい. (default: DA)
  --verbose        配属結果を標準出力します. (default: False)
```

`--input`に指定するjsonファイルは以下のように記述します.

```json
{
  "students": {
    "Student_0": {
      "choice": {
        "Teacher_1": 2,
        "Teacher_2": 1
      }
    },
    "Student_1": {
      "choice": {
        "Teacher_0": 2,
        "Teacher_1": 1
      }
    }
  },
  "teachers": {
    "Teacher_0": {
      "capacity": 0,
      "preference": {
        "Student_0": 1,
        "Student_1": 2
      }
    },
    "Teacher_1": {
      "capacity": 1,
      "preference": {
        "Student_0": 1,
        "Student_1": 2
      }
    },
    "Teacher_2": {
      "capacity": 1,
      "preference": {
        "Student_0": 1,
        "Student_1": 2
      }
    }
  }
}
```

"Student_1"や"Teacher_1"等はそれぞれ生徒, 教員の名前に該当します. 各生徒名が持つ"choice"のvalueには, 生徒が志望する教員とその教員の志望順位がペアで記録されています. 各教員名が持つ"capacity"のvalueには, その教員が受け持てる学生の定員数が記録されており, "preference"のvalueには, その教員が選好する学生とその学生の選好順位がペアで記録されています. 選好順位は, 例えば, 成績順で設定します.


`--method`には, 研究室配属を計算するアルゴリズムを指定します. 指定可能なそれぞれのアルゴリズムはcalc_assignment_tools.pyに実装されています. 以下は各アルゴリズムの説明です.

- DA: deferred acceptance algorithmにより配属を決定する.
- MNK: munkresモジュールを用いて割当問題の最適解を1つだけ導く.
- HNG: ハンガリー法を用いて割当問題の最適解を全て導く. 

## デモデータの作製

make_demodata.pyを用いて研究室配属問題のデモデータを作ることが出来ます.

```bash
$ # デモデータ作製.
$ python lab-assignment-problem/src/make_demodata.py --opt separate --output output
$ # outputディレクトリ直下に配属結果が出力されます.
$ ls output
demodata_separate.json
```

make_demodata.pyのヘルプは次のコマンドで確認できます.

```bash
$ python lab-assignment-problem/src/make_demodata.py --help
usage: make_demodata.py [-h] [--output DIR] [--ns INT] [--nt INT]
                        [--limit INT] [--opt STRING]

研究室配属のデモデータを作製するスクリプト.

optional arguments:
  -h, --help    show this help message and exit
  --output DIR  出力ディレクトリを指定して下さい. (default: ./)
  --ns INT      生徒数を指定して下さい. (default: 20)
  --nt INT      教員数を指定して下さい. (default: 15)
  --limit INT   志望順位の数を指定して下さい. (default: 10)
  --opt {random,separate}
                デモデータ作製時のオプションを指定して下さい. (default: random)
```

`--opt`には, デモデータ作製時のオプションを指定します. 以下は各オプションの説明です.

- random: 全ての生徒が教員に対する志望順位をランダムに決定する.
- separate: DAを用いた場合, 全ての生徒が第1志望の教員に配属される解が導かれる.

## csvファイルをmain.pyの入力に使えるjsonファイルに変換

convert2json.pyを用いて, `.xlsx`, `.xls`, `.csv`, `.tsv`のいずれかのフォーマットで作製した次の形式の表をmain.pyの`--input`に指定可能なjsonファイルに変換出来ます.

|　||||||
|--|--|--|--|--|--|
||choice|||||
||1|2|3|||
|Student_1|Teacher_1|Teacher_2|Teacher_3|||
|Student_2|Teacher_1|Teacher_3|Teacher_4|||
|Student_3|Teacher_2|Teacher_1|Teacher_5|||
|Student_4|Teacher_3|Teacher_1|Teacher_2|||
|　||||||
||capacity|preference||||
|||1|2|3|4|
|Teacher_1|2|Student_1|Student_2|Student_4|Student_3|
|Teacher_2|1|Student_1|Student_2|Student_4|Student_3|
|Teacher_3|2|Student_1|Student_2|Student_4|Student_3|
|Teacher_4|2|Student_1|Student_2|Student_4|Student_3|
|Teacher_5|0|Student_1|Student_2|Student_4|Student_3|

学生に対する教員の選好順位の数は生徒数と等しく成るように記述して下さい.


上の形式の表を, 例えば, table.xlsで保存してconvert2json.pyにより変換すると, 以下のようなjsonファイルが作製されます.

```bash
$ python lab-assignment-problem/src/convert2json.py --input table.xls --output output
$ ls output
table.json
$ cat output/table.json 
{
  "students": {
    "Student_1": {
      "choice": {
        "Teacher_1": 1,
        "Teacher_2": 2,
        "Teacher_3": 3
      }
    },
    "Student_2": {
      "choice": {
        "Teacher_1": 1,
        "Teacher_3": 2,
        "Teacher_4": 3
      }
    },
    "Student_3": {
      "choice": {
        "Teacher_1": 2,
        "Teacher_2": 1,
        "Teacher_5": 3
      }
    },
    "Student_4": {
      "choice": {
        "Teacher_1": 2,
        "Teacher_2": 3,
        "Teacher_3": 1
      }
    }
  },
  "teachers": {
    "Teacher_1": {
      "capacity": 2,
      "preference": {
        "Student_1": 1,
        "Student_2": 2,
        "Student_3": 4,
        "Student_4": 3
      }
    },
    "Teacher_2": {
      "capacity": 1,
      "preference": {
        "Student_1": 1,
        "Student_2": 2,
        "Student_3": 4,
        "Student_4": 3
      }
    },
    "Teacher_3": {
      "capacity": 2,
      "preference": {
        "Student_1": 1,
        "Student_2": 2,
        "Student_3": 4,
        "Student_4": 3
      }
    },
    "Teacher_4": {
      "capacity": 2,
      "preference": {
        "Student_1": 1,
        "Student_2": 2,
        "Student_3": 4,
        "Student_4": 3
      }
    },
    "Teacher_5": {
      "capacity": 0,
      "preference": {
        "Student_1": 1,
        "Student_2": 2,
        "Student_3": 4,
        "Student_4": 3
      }
    }
  }
}
```

convert2json.pyのヘルプは次のコマンドで確認出来ます.

```bash
$ python lab-assignment-problem/src/convert2json.py --help
usage: convert2json.py [-h] --input FILE [--output DIR]

xlsxやxls, csv, tsvファイルを変換して, main.pyの入力に指定可能なjsonファイルを出力するスクリプト.

optional arguments:
  -h, --help    show this help message and exit
  --input FILE  入力ファイルを指定して下さい. (default: None)
  --output DIR  出力ディレクトリを指定して下さい. (default: ./)
```