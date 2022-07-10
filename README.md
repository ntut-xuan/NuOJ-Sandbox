# NuOJ - Sandbox

## Introduction

NuOJ 所使用的沙盒系統，使用 POST 傳送程式碼與測資，不需要 Database，基於 IOI 的 Isolate 開源專案進行開發。

![img](https://camo.githubusercontent.com/d17ced33372b5d685500dcf5c8ece597ef15fd805aa1f0b767ebc6042307824b/68747470733a2f2f692e696d6775722e636f6d2f59487457364b6a2e706e67)





## 安裝

```
sudo apt-get install make
wget https://raw.githubusercontent.com/ntut-xuan/NuOJ-Sandbox/main/Makefile
sudo make
```



## 安裝環境

|     環境     |      |
| :----------: | :--: |
| Ubuntu 22.04 |  ✅   |
| Ubuntu 20.04 |  ✅   |



## 支援操作

|   操作   | 支援 |
| :------: | :--: |
| 編譯測試 |  ✅   |
| 運行測試 |  ✅   |
| 評測測試 |  ✅   |
| 測資驗證 |      |



## 支援語言

|  語言  | 支援 |
| :----: | :--: |
|  C++   |  ✅   |
|  Java  |      |
| Python |      |



## 使用

使用 POST 來進行程式評測。



### POST URL

```
https://localhost:3355/judge
```



### POST Data

NuOJ-Sandbox 使用 JSON 格式的 Data 來進行操作，如下：

```json
{
	"code": "...",
	"solution": "...",
	"checker": "...",
	"execution": "...",
	"option": {},
	"testcase": [
		"<testcase1>",
		"<testcase2>"
	]
}
```



#### Code

一個字串，為待評測的程式。



#### Solution

一個字串，為題目解答的程式。



#### Checker

一個字串，為判定答案是否正確的程式，可支援 [Testlib by MikeMirzayanov](https://github.com/MikeMirzayanov/testlib)。

提交的程式須能符合 `checker.o <input_file> <output_file> <ans_file>`，例如

```bash
./checker.o 1.in 1.out 1.ans
```



#### Execution

為一個字串，放入沙盒運行的模式。

| 模式 | 意義 |
| :--: | :--: |
|  C   | 編譯 |
|  E   | 運行 |
|  J   | 評測 |



#### Testcase

為一序列，序列中的每個元素為一筆測試資料，例如：

```json
{
    "testcase": ["2\n1 2", "3\n1 2 3", "4\n1 2 3 4"]
}
```

```json
{
    "testcase": ["2\n2 3 5\n2 3 6", "2\n2 4 4\n2 5 5"]
}
```

#### Option

為一字典，用來設定選項。

##### threading

用來設定是否要創立執行緒來執行，若為 `False` 則 POST 會需要等評測結束後才會得到結果，會花較長的時間。
若 `True` 則 POST 會回傳是否 POST 成功，評測結果需要由 /result/<tracker_ID> 來得到結果。

### POST Data Require

| 操作 |        code        |      solution      |      checker       |     execution      |      testcase      |      option        |
| :--: | :----------------: | :----------------: | :----------------: | :----------------: | :----------------: | :----------------: |
| 評測 | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | 
| 執行 | :white_check_mark: |  |                    | :white_check_mark: | :white_check_mark: | :white_check_mark: | 
| 編譯 | :white_check_mark: |                    |                    | :white_check_mark: |                    | :white_check_mark: | 



### POST Response

#### Compile

> <待補>



#### Execution

> <待補>



#### Judge

> <待補>
