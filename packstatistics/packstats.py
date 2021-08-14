"""Debian Package Statistics CLI Tool"""

import gzip, argparse, os, urllib.request, pathlib
from collections import defaultdict
from packstats.exceptions import ContentIndexForArchitectureNotFound


def parse_contents_index(contents_index_file: str) -> dict:
    """Parses a given contents index file and returns a dictionary with the
    package names and their associated files

    Arguments:

        contents_index_file: path of the content index file to be parsed.

    Returns:
        dict: a dictionary containing the packages as keys and
              a list of associated files as the values
    """
    with open(contents_index_file) as buffer:
        package_dict = defaultdict(list)
        for line in buffer:
            line = line.strip()
            if line == "":
                continue
            file_name, packages = line.rsplit(" ", maxsplit=1)
            packages = packages.split(",")
            for package in packages:
                if file_name != "EMPTY_PACKAGE":
                    package_dict[package].append(file_name)
    return package_dict
    
def get_content_files_list(copy_url: str) -> list:
    with urllib.request.urlopen(copy_url) as response:
        raw_html = response.read()
    html = raw_html.decode()

    content_types = []
    for line in html.split("\r\n"):
        if line.startswith("<a href=\"Contents-"):
            filename = line[line.find("Contents-"):line.find(".gz")+3]
            url = f"{copy_url}{filename}" if copy_url.endswith(
                "/") else f"{copy_url}/{filename}"
            arch = filename[filename.rfind("-")+1:filename.rfind(".gz")]
            content_types.append(dict(filename=filename, url=url, arch=arch))
    return content_types


def download_contents_file(
        content_file_url: str, output_dir: str = None,
        reuse_if_present: bool = False) -> str:
    if output_dir is None:
        output_dir = os.getcwd()
    basename = os.path.basename(content_file_url)
    file_name = os.path.splitext(basename)[0]

    output_gz_file = pathlib.Path(output_dir) / basename
    output_file = pathlib.Path(output_dir) / file_name
    if output_file.exists():
        if reuse_if_present:
            return output_file

    with urllib.request.urlopen(content_file_url) as response:
        data = response.read()
    with open(output_gz_file, "wb") as buffer:
        buffer.write(data)

    with gzip.open(output_gz_file, "rb") as buffer:
        data = buffer.read()
    with open(output_file, "wb") as buffer:
        buffer.write(data)

    return output_file


def get_contents_file_urls(arch: str, copy_url: str, include_udeb: bool = False) -> list:
    contents_file_list = get_content_files_list(copy_url)
    urls = []
    for file in contents_file_list:
        url = file["url"]
        filename = file["filename"]
        file_arch = file["arch"]
        is_udeb = filename.endswith(f"udeb-{file_arch}.gz")
        if arch == file_arch:
            if is_udeb:
                if include_udeb:
                    urls.append(url)
            else:
                urls.append(url)
    return urls



def main(
        copy_url: str, arch: str, count: int, include_udeb: bool,
        sort_increasing: bool, output_dir: str, reuse_if_present: bool) -> None:
    arch = arch.lower()  # use lowercase for the architecture.
    # get a list of content index urls
    content_indices_urls = get_contents_file_urls(
        arch, copy_url, include_udeb)

    if len(content_indices_urls) == 0:
        # if the architecture didn't retrieve anything, output an error,
        # with a list of architectures
        content_indices = get_content_files_list(copy_url)
        found_architectures = sorted({item["arch"] for item in content_indices})
        found_architectures = ", ".join(found_architectures)
        # raise a custom exception
        raise ContentIndexForArchitectureNotFound(
            f"{arch} was not found in the given mirror. "
            f"Available architectures are: {found_architectures}")

    # prepare to summarize the data
    complete_package_data = {}
    for url in content_indices_urls:
        content_index_file = download_contents_file(
            url, output_dir=output_dir, reuse_if_present=reuse_if_present)
        print(content_index_file)
        package_data = parse_contents_index(content_index_file)
        complete_package_data.update(**package_data)

    package_list = complete_package_data.keys()
    # sort them in the descending order of the number of packages
    # unless the user wants the ascending order
    package_list = sorted(
        package_list, key=lambda x: len(complete_package_data[x]), reverse=not sort_increasing)

    # print the output, only print how many ever the user asks through the count argument

    for ix, package in enumerate(package_list):
        if ix == 0:
            print(f"{'No.':<10}\t{'Package Name':<50}\tFile Count")
        print(f"{ix+1:<10}\t{package:<50}\t{len(complete_package_data[package])}")
        if ix+1 == count:
            break
            # use this instead of slicing the reversed list because this way,
            # the overhead of converting a giant iterator to a list is avoided.
            # Some milliseconds may be saved.


def cli_main():
    """Command line interface function"""
    parser = argparse.ArgumentParser(
        description=(
            "A tool to get the package statistics by parsing "
            "a Contents Index "
            "(defined here - https://wiki.debian.org/RepositoryFormat#A.22Contents.22_indices)"
            "from a debian mirror, given a system architecture."
        )
    )
    parser.add_argument(
        "arch", type=str,
        help="indicate the architecture of the Contents index.")
    parser.add_argument(
        "-m", "--copy_url", type=str,
        default="http://ftp.uk.debian.org/debian/dists/stable/main/",
        help=(
            "Mirror URL from which to fetch the contents file. "
            "DEFAULT http://ftp.uk.debian.org/debian/dists/stable/main/")
    )
    parser.add_argument(
        "-u", "--include-udeb",
        help="include udeb file for the given architecture. DEFAULT False",
        action="store_true")
    parser.add_argument(
        "-c", "--count", type=int, default=10,
        help="number of packages to list. Use -1 to list all. DEFAULT 10")
    parser.add_argument(
        "-i", "--sort-increasing", action="store_true",
        help="Sort package stats list by increasing number of files. DEFAULT False")
    parser.add_argument(
        "-o", "--output-dir", type=str, default=os.getcwd(),
        help=(
            "enter the directory in which to store the downloaded contents indices. "
            "DEFAULT <current-directory>"
            )
        )
    parser.add_argument(
        "-r", "--reuse-if-exists",
        help=(
            "This helps to reuse a content file if it has been downloaded previously and "
            "exists in the output directory."
            ),
        action="store_true",
    )
    args = parser.parse_args()
    main(
        copy_url=args.copy_url,
        arch=args.arch,
        include_udeb=args.include_udeb,
        sort_increasing=args.sort_increasing,
        count=args.count,
        output_dir=args.output_dir,
        reuse_if_present=args.reuse_if_present,
    )
