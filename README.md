# lab-assignment-problem
特研生の研究室配属を決定するスクリプト.

次のようにレポジトリをクローンして, main.pyにより研究室配属を計算し標準出力します.

```bash
$ # レポジトリをクローン.
$ git clone https://github.com/tmurakami1234/lab-assignment-problem.git
$ # python3.6以上でスクリプトを実行.
$ python lab-assignment-problem/src/main.py --input input.json
```

`--input`に指定するjsonファイルは以下のように記述します.

```bash
$ cat input.json
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
