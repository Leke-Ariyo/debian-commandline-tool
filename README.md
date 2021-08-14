# Canonical Interview Question: Debian Package Statistics

## Instructions

Debian uses *deb packages to deploy and upgrade software. The packages
are stored in repositories and each repository contains the so called "Contents
index". The format of that file is well described here
https://wiki.debian.org/RepositoryFormat#A.22Contents.22_indices

Your task is to develop a python command line tool that takes the
architecture (amd64, arm64, mips etc.) as an argument and downloads the
compressed Contents file associated with it from a Debian mirror. The
program should parse the file and output the statistics of the top 10
packages that have the most files associated with them.
An example output could be:

./package_statistics.py amd64

1. <package name 1>         <number of files>
2. <package name 2>         <number of files>
......
10. <package name 10>         <number of files>

You can use the following Debian mirror
http://ftp.uk.debian.org/debian/dists/stable/main/. Please do try to
follow Python's best practices in your solution. Hint: there are tools
that can help you verify your code is compliant. In-line comments are
appreciated.

It will be good if the code is accompanied by a 1-page report of the
work that you have done including the time you actually spent working on it.

Once started, please return your work in approximately 24 hours.

Note: the focus is not to write the perfect Python code, but to see how
you'll approach the problem and how you organize your work.


## Assumptions

Ubuntu currently ships Python3, so I will use it. Python 2 suppport is possible, but out of the scope of this solution.

I am not using any 3rd party applications for the core application. The performance could be improved using other packages, or other versions of Python (perhaps PyPy).


### Regarding `udeb` content indices

I am treating the `udeb` files as additional sources, which can be included in the
report for an architecture by means of an `--include-udeb` flag.
Check the help output for more information.

## Application Installation

If you would like to install this application into your python3 environment, run the following:

```bash
python3 setup.py install
```

*Note that the installation is not necessary to run this application*.

## Usage

### With Installation

Once `packstats` is installed, you can run it in one of two ways.

```packstats --help```

Or:

```python -m packstats --help```

The second version is preferred in places where you would want to *ensure* the right version of python is being used, perhaps with a virtal environment.

### Without Installation

If you want to run `packstats` without installation, use the helper file instead.

Either modify permissions to make it executable and use a version of python3 to run it:

```bash
chmod +x package_statistics.py
./package_statistics.py --help
```

Or, you can run it with the python command directly.

```bash
python3 package_statistics.py
```

## `packstats` CLI

The command line interface has a help command that teaches you what you can do with the tool.

```
$ python package_statistics.py --help
usage: package_statistics.py [-h] [-m MIRROR_URL] [-u] [-c COUNT] [-i]
                             [-o OUTPUT_DIR] [-r]
                             arch

A tool to get the package statistics by parsing a Contents Index (defined here
- https://wiki.debian.org/RepositoryFormat#A.22Contents.22_indices)from a
debian mirror, given a system architecture.

positional arguments:
  arch                  the architecture of the Contents index you would like
                        to parse.

optional arguments:
  -h, --help            show this help message and exit
  -m MIRROR_URL, --copy_url MIRROR_URL
                        Mirror URL from which to fetch the contents file.
                        DEFAULT
                        http://ftp.uk.debian.org/debian/dists/stable/main/
  -u, --include-udeb    include udeb file for the given architecture. DEFAULT
                        False
  -c COUNT, --count COUNT
                        number of packages to list. Use -1 to list all.
                        DEFAULT 10
  -i, --sort-increasing
                        Sort package stats list by increasing number of files.
                        DEFAULT False
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        a directory in which to store the downloaded contents
                        indices. DEFAULT <current-directory>
  -r, --reuse-if-exists
                        Reuses a content file if it has been downloaded
                        previously and exists in the output directory.
```


## Examples

### Getting `armel` Statistics

$ packstats armel


### Getting the top 25 packages

$ packstats -c 25 armel


### Getting `amd64` packages, with `udeb` files included

$ packstats --include-udeb amd64


### Redirecting Downloaded Files to `/tmp`

```
$ packstats -o /tmp armel
No.	Package Name                                      	File Count
1.	fonts/fonts-cns11643-pixmaps                      	110999
2.	x11/papirus-icon-theme                            	69475
3.	fonts/texlive-fonts-extra                         	65577
4.	games/flightgear-data-base                        	62463
5.	devel/piglit                                      	49913
6.	doc/trilinos-doc                                  	49591
7.	x11/obsidian-icon-theme                           	48829
8.	games/widelands-data                              	34984
9.	doc/libreoffice-dev-doc                           	33667
10.	misc/moka-icon-theme                              	33326
```
This downloads all files in the given directory. In this case: `/tmp`.

### Reusing Downloaded Files


```
$ packstats -r amd64
```




## Development and Testing

To understand how `packstats` is implemented, I recommend beginning with `packstats.packstats.cli_main`,
which builds an `argparse` command line interface.

From there, the arguments are sent to `packstats.packstats.main`. This builds a workflow with the internal
functions which are self-explanatory if you look at the docstrings.

For the formatting, I always auto-run autopep8 on my code, and then check the score with pylint which
lints as I type in VS Code.

### Testing

$ python setup.py test


The tests can also be run with `pytest`, should you choose to install it.


## Profiling with `py-spy`


$ py-spy top -- python package_statistics.py amd64

