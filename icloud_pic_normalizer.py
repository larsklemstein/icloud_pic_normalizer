#!/usr/bin/env python3

import os
import os.path
import re
import logging

from typing import Tuple, Callable


def file_sizes_from_dir(
        dir: str,
         filter_by: re.Pattern = None,
         min_size: int =0) -> Tuple[Tuple[str, int], ...]:
    """Returns a tuple of file, filesize pairs for dir
    """

    logger = logging.getLogger()

    file_sizes = []

    logger.debug(f'scan objects in dir "{dir}"')

    for object in os.listdir(dir):
        logger.debug(f'inspect object "{object}')
        
        fqfn = os.path.join(dir, object)
        if not os.path.isfile(fqfn):
            logger.debug(f' -> skip "{object}", is not a file')
            continue

        file_stat = os.stat(fqfn)
        file_size = file_stat.st_size

        if file_size < min_size:
            logger.debug(f' -> skip "{object}", size {file_size} is '
                         f'under minimum of {min_size}')
            continue

        if filter_by is not None and not filter_by.match(object):
            logger.debug(f' -> skip "{object}", does not match pattern')
            continue

        logger.debug(f'  + "{object}"')
        file_sizes.append((fqfn, file_size))

    logger.info(f'have {len(file_sizes)} matching files in total')

    return tuple(file_sizes)


def files_grouped_by_size(file_sizes: Tuple[Tuple[int, str], ...]):
    """Create groups of files in the form tuple(file_tuple, common_size)
    """
    file_size_dict = dict()
    file_sizes_multi = list()

    logger = logging.getLogger()
    logger.info(f'got {len(file_sizes)} files to group(s) by size')

    for file_fqfn_with_size in file_sizes:
        fqfn, size = file_fqfn_with_size[:]
        if not size in file_size_dict:
            file_size_dict[size] = list()
        
        file_size_dict[size].append(fqfn)
    
    for (size, file_list) in file_size_dict.items():
        file_sizes_multi.append((tuple(file_list), size))

    raw_files_with_sizes =  tuple(file_sizes_multi)
    logger.info(f'prodcuced {len(raw_files_with_sizes)} file group(s)')

    return raw_files_with_sizes


def file_groups_matching_condition(
        cond: Callable,
        file_sizes: Tuple[Tuple[int, str]]
    ):

    assert isinstance(file_sizes, tuple)

    logger = logging.getLogger()

    file_groups_filtered = list()

    logger = logging.getLogger()
    logger.info(f'got {len(file_sizes)} file groups')

    for fg in file_sizes:
        if cond(fg):
            file_groups_filtered.append(fg)
    
    logger.info(f'have now {len(file_groups_filtered)} file group(s) left')

    return tuple(file_groups_filtered)


def file_groups_with_at_least(amount: int, file_sizes: Tuple[Tuple[int, str]]):
    return file_groups_matching_condition(
        lambda fg: len(fg[0]) >= amount, file_sizes)


def file_groups_with_exactly(amount: int, file_sizes: Tuple[Tuple[int, str]]):
    return file_groups_matching_condition(
        lambda fg: len(fg[0]) == amount, file_sizes)


if __name__ == '__main__':
        import sys

        logging.basicConfig(
            level=logging.DEBUG,
            format=('%(levelname)s - %(asctime)s - %(funcName)s() '
                    '@ %(lineno)s - %(message)s'),
        )

        if len(sys.argv) != 2:
            raise SystemError('Need a directory argument')
        
        dir = sys.argv[1]

        filter = re.compile(r'.+\.(?:py|txt)$')
        fs = file_sizes_from_dir(dir, filter_by=filter, min_size=10)

        fsg = files_grouped_by_size(fs)

        fsg = file_groups_with_at_least(2, fsg)
        print('-->', fsg)
