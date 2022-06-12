# Sorting Data of Files 📊

### Version 1.0

To read information from various files with extensions: csv, json and xml. In order to combine them into a single output file, for now in format tsv.

The files must to have the same metadata, i.e. the data within the files is structured in a similar way.

<br/>

## Description

It's a little application that runs in a CLI/Terminal through a python script.

It was created using:

* [Python] v3(.10) como lenguaje de programación.

The only third party application used is [ijson]. With the goal of not loading the whole json file into memory (the files can be GB in size).

The specific version is in _requirements.txt_.

<br/>

It was created following the PEP8 rules/recommendations about code foramting. Although 120 is used as the limit of characters per line.

The docstrings follow what is indicated by the PEP257 with a NumPy format. **The six modules have docstrings**

<br/>

## Installation

To use it, you need to clone the repository into a folder. If you do not want to modify the python packages installed in the OS, create a virtual environment using python's 'venv'.

To this, type next commands in a CLI/terminal.

    > cd path_where_repository_was_cloned/
    > python -m pip install venv
    > python -m venv virtual_env_name

Now activate the virtual environment (linux):

    > . virtual_env_name/bin/activate

Then proceed to update the pip in the virtual environment. Since many times, the virtual machine is created with an old version of pip.

    > pip install --upgrade pip

Finally, you must to to install [ijson] (using requirements.txt file).

    > pip install -r requirements.txt

<br/>

## ** Running the program ** 💻

It runs like any python script. The main script is _main.py_ and it will be found in the src folder.

    > cd src
    > python main.py
** _To be able of select the default 'data' directory when running it, do not forget write the first command._

A menu is displayed with these two options: enter the path of the data folder and process the data, along with a third one to exit the program.

![menu](https://github.com/Jony-softdeveloper/Sorting-data-of-files/blob/main/images/1%20Menu.png)

Simply enter the desired option.

Obviously, it is nos possible choose option two, without first entering the directory of the (data) files.

![Error 1](https://github.com/Jony-softdeveloper/Sorting-data-of-files/blob/main/images/2%20Error%20-%20select%20sort%20data.png)

Select the first option and it will display a question about using the _data/_ directory as a working directory. If so, you can immediately continue with the sorting process.

The result will save inside the work directory _result/result.tsv_.

![Data](https://github.com/Jony-softdeveloper/Sorting-data-of-files/blob/main/images/3%20Process%20data.png)

Besides, it is possible to work in different (data) directories (Enter the absolute path to it).

![Other Data](https://github.com/Jony-softdeveloper/Sorting-data-of-files/blob/main/images/5%20Process%20other%20data.png)

<br/>

## **Performance**
The performance is acceptable. Considering that my laptop is ten years old right now.

Some CPU specifications (_cat /proc/cpuinfo_ && _lscpu_):
* model name	: AMD A4-3300M APU with Radeon(tm) HD Graphics
* cpu MHz		: 1031.560
* cache size	: 1024 KB
* Architecture  : x86_64
* Cpu(s)        : 2 cores with the same features
* Thread(s) per core    : 2
* «Socket(s)»   : 1
With 8 GB of RAM (DDR3).

With provided data takes around **10 ms** to process them and generate the tsv file.

Execute it two times (measure with _perf_counter_ns()_ of _time_ module).

![Performance Data 1](https://github.com/Jony-softdeveloper/Sorting-data-of-files/blob/main/images/6%20Measure%201%20data.png)

![Performance Data 2](https://github.com/Jony-softdeveloper/Sorting-data-of-files/blob/main/images/7%20measure%202%20data.png)

A second directory 'data2_test' with two more files: hola.txt (ignored by the program) and json_data_2 (with about 2900 more records). Also, 'csv_data_1' was edited to have 4005 records/rows, but withouh header 'M2'. That is, **about 7000 data were processed**.

This times, it was measure with 'time' command too.

    > time python main.py

![Performance Other data 1](https://github.com/Jony-softdeveloper/Sorting-data-of-files/blob/main/images/8%20Measure%201%20data2.png)

![Performance Other data 2](https://github.com/Jony-softdeveloper/Sorting-data-of-files/blob/main/images/9%20Measure%202%20data2.png)

With an average of **310 ms**. That match with _user_ + _sys_ times ≈ **410 ms**.

<br/>

##  Improvements

> Perform a final reordering when records exceed 52 thousand. Being able to even save first in temporary files, and then in the final file.

> It remains to develop unit tests for the functions and methods of the classes. It is recommended to use the [Pytest] package to perform them.

<br/>

## Credits

Author: Jonathan Garcia S. @Jony-softdeveloper

## License

This project is [licensed] under the terms of the **MIT License**.

[Python]: https://www.python.org/downloads/ "Python"
[ijson]: https://github.com/ICRAR/ijson "ijson"
[licensed]: https://github.com/Jony-softdeveloper/Sorting-data-of-files/blob/main/LICENSE "licensed"
