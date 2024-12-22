"""
Reproduce by me the source code in: https://github.com/python/cpython/blob/3.13/Lib/tokenize.py#L486
to catch error at many position in file
"""

import os
import io
import sys
import tokenize
import re
import itertools
from typing import List


def file2entities(total_lines: List[str])->List[str]:
    """Split code file into functions, classes, 
    function with decoration
    """
    # get index of class, function, decorator
    split_lines_ids = [ ith
                    for ith, line in enumerate(total_lines)
                    if re.search(r"\bclass|\bdef|\@(.*?)\w", line) is not None
    ]
    
    # drop
    drop_iths = []
    for ith in range(len(split_lines_ids)-1):
        if split_lines_ids[ith] + 1 == split_lines_ids[ith+1]:
            drop_iths.append(ith+1)

    # finall split idx, plus with final index before make pairwise
    new_split_ids = [idx for ith, idx in enumerate(split_lines_ids) if ith not in drop_iths] + [len(total_lines)-1]

    # segmentation
    segments = []
    for start_idx, end_idx in itertools.pairwise(new_split_ids):
        segments.append("".join(total_lines[start_idx: end_idx]))

    # merge many segments together, batch = 2 -> merge 2 functions
    return ["\n".join(segments[i: i+2]) for i in range(0, len(segments),2)]


def entity_check(string_content:str):
    # convert string to bytes
    string_in_bytes = str.encode(string_content)

    # makeup text stream
    buffer = io.BytesIO(string_in_bytes)

    # detect encoding
    encoding, lines = tokenize.detect_encoding(buffer.readline)
    buffer.seek(0)
    # convert to io.textIOWarpper
    f = io.TextIOWrapper(buffer, encoding, line_buffering=True)
    
    try:
        # force to loop over token generato
        list(tokenize.generate_tokens(f.readline))

    except IndentationError as e:
        return {
            'line_number': e.lineno,
            'code_error': e.text
        }


def checker(file:str)->List[Dict[str,str]]:
    """
    Function to check indentation of python code
    Args:
        - file: system path (can be relative) for open and read
    """
    # get lines in file
    with open(file,'r') as fp:
        total_lines = fp.readlines()

    # segmentation
    segments = file2entities(total_lines)

    # find indent error in all lines
    total_errors = []
    for ith, str_func in enumerate(segments):
        total_errors.append(entity_check(str_func))

    return [ele for ele in total_errors if ele is not None]


