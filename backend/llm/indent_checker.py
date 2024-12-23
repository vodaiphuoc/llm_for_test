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
from typing import List, Dict, Literal, Union
import ast
from copy import deepcopy

# def file2entities(total_lines: List[str])->List[str]:
#     """Split code file into functions, classes, 
#     function with decoration
#     """
#     # get index of class, function, decorator
#     split_lines_ids = [ ith
#                     for ith, line in enumerate(total_lines)
#                     if re.search(r"\bclass|\bdef|\@(.*?)\w", line) is not None
#     ]
    
#     # drop
#     drop_iths = []
#     for ith in range(len(split_lines_ids)-1):
#         if split_lines_ids[ith] + 1 == split_lines_ids[ith+1]:
#             drop_iths.append(ith+1)

#     # finall split idx, plus with final index before make pairwise
#     new_split_ids = [idx for ith, idx in enumerate(split_lines_ids) if ith not in drop_iths] + [len(total_lines)-1]

#     # segmentation
#     segments = []
#     for start_idx, end_idx in itertools.pairwise(new_split_ids):
#         segments.append("".join(total_lines[start_idx: end_idx]))

#     # merge many segments together, batch = 2 -> merge 2 functions
#     return ["\n".join(segments[i: i+2]) for i in range(0, len(segments),2)]


# def entity_check(string_content:str):
#     # convert string to bytes
#     string_in_bytes = str.encode(string_content)

#     # makeup text stream
#     buffer = io.BytesIO(string_in_bytes)

#     # detect encoding
#     encoding, lines = tokenize.detect_encoding(buffer.readline)
#     buffer.seek(0)
#     # convert to io.textIOWarpper
#     f = io.TextIOWrapper(buffer, encoding, line_buffering=True)
    
#     try:
#         # force to loop over token generato
#         list(tokenize.generate_tokens(f.readline))

#     except IndentationError as e:
#         return {
#             'line_number': e.lineno,
#             'code_error': e.text
#         }
#     except tokenize.TokenError as e:
#         pass


# def checker(file:str)->List[Dict[str,str]]:
#     """
#     Function to check indentation of python code
#     Args:
#         - file: system path (can be relative) for open and read
#     """
#     print('checker run: ',file)
#     # get lines in file
#     with open(file,'r') as fp:
#         total_lines = fp.readlines()

#     # segmentation
#     segments = file2entities(total_lines)

#     # find indent error in all lines
#     total_errors = []
#     for ith, str_func in enumerate(segments):
#         total_errors.append(entity_check(str_func))

#     print('checker end: ',file)

#     _filter_list = [ele for ele in total_errors if ele is not None]
#     return _filter_list if len(_filter_list) > 0 else True



class Segment(object):
    """Segment object can be used 
    represent errors for classes (contains __init and other methods) 
    or functions.
    """
    def __init__(self, 
                 code_lines: List[str], 
                 start_line:int
                 ) -> None:

        if re.search(r"(.*?)class", "".join(code_lines)) is not None:
            self.segment_type = 'class'
        else:
            self.segment_type = 'function'

        self.code_lines = code_lines
        self.start_line = start_line

        if self.segment_type == 'class':
            if re.search(r"\@dataclass", "".join(code_lines)) is not None:
                self._is_dataclass = True
                self.class_def_line = "".join(self.code_lines)
            else:
                self._is_dataclass = False
                method_params = IndentChecker.file2entities(self.code_lines[1:], function_type='method')

                if len(init_param_ith:= [ith for ith, param in enumerate(method_params) 
                                    if '__init__' in "".join(param['code_lines'])]) > 0:
                    self.class_def_line = "".join(self.code_lines[0: init_param_ith[0]])
                    method_params.pop(init_param_ith[0])
                    self.methods = deepcopy(method_params)
                else:
                    self.class_def_line = "".join(self.code_lines[0: method_params[1]['start_line']])
                    method_params.pop(0)
                    self.methods = method_params
                

        self.errors = []
        self.run_check()

    def __repr__(self) -> str:
        """this is used for debugging only"""
        if len(self.errors) > 0:
            repr_errors = "\n".join([f"line: {ele['line_number']} \ncode: \n{ele['code_error']}"
                                 for ele in self.errors])
        else:
            repr_errors = 'True'

        return f"""
-------------------------------------------------------------
**segment type: {self.segment_type}
**start line content: {self.class_def_line if self.segment_type == 'class' else ''}
**start line in file: {self.start_line}
**code content:
{"".join(self.code_lines)}
** methods:
{self.methods if self.segment_type == 'class' and not self._is_dataclass else ''}
**error:
{repr_errors}
-------------------------------------------------------------
"""

    def entity_check(self, 
                     builed_string:str, 
                     start_line:str
                     )->Dict[str,Union[str,int]]:        
        try:
            tree = ast.parse(builed_string)
        except IndentationError as e:
            return {
                'line_number':e.lineno + start_line - 1, 
                'code_error': e.text
            }
        except SyntaxError as e:
            return None

    def run_check(self):
        if self.segment_type == 'function':
            _status = self.entity_check(builed_string = "".join(self.code_lines), 
                                      start_line = self.start_line)
            if _status is not None:
                self.errors.append(_status)
        
        else:
            try:
                ast.parse(self.class_def_line)
                if not self._is_dataclass:
                    for method_seg in self.methods:
                        _status = self.entity_check(builed_string = self.class_def_line + "".join(method_seg['code_lines']), 
                                                start_line = method_seg['start_line'] + self.start_line)
                        if _status is not None:
                            self.errors.append(_status)
            
            except IndentationError as e:
                # handle exception when class definition is wrong
                self.errors.append({
                'line_number': self.start_line, 
                'code_error': e.text
            })

    
    def get_error_dict(self):
        return {_error['line_number']:_error['code_error'] for _error in self.errors}

class IndentChecker(object):

    @staticmethod
    def _get_class_function(line:str,index:int, prev_line:str,prev_index:int):
        if re.search(r"^\s{0,8}class\s(.*?)\:|(.*?)def\s(.*?)\)\:", line) is not None \
            and re.search(r"(.*?)\(self", line) is None \
            and re.search(r"\@classmethod|\@staticmethod", prev_line) is None:
                if re.search(r"(.*?)\@(.*?)\n", prev_line) is not None:
                    return prev_index
                else:
                    return index
        else:
            return None

    @staticmethod    
    def _get_class_method(line:str,index:int, prev_line:str,prev_index:int):
        if re.search(r"\s+def\s(.*?)\)\:", line) is not None:
            if re.search(r"(.*?)\(self", line) is not None:
                return index
            elif re.search(r"\@classmethod|\@staticmethod", prev_line) is not None:
                return prev_index
        else:
            return None

    @staticmethod
    def file2entities(total_lines: List[str], 
                      function_type: Literal['normal','method'] = 'normal'
                      )->List[Dict[str, str]]:
        """Split code file into functions, classes, 
        function with decoration
        """
        # get index of class, function, decorator
        pattern_function = IndentChecker._get_class_function if function_type == 'normal' \
            else IndentChecker._get_class_method
        
        split_lines_ids = [ _index
                        for ith, line in enumerate(total_lines)
                        if (_index:= pattern_function(line, ith,total_lines[ith-1], ith-1)) is not None
        ]
        
        # drop
        drop_iths = []
        # for ith in range(len(split_lines_ids)-1):
        #     if split_lines_ids[ith] + 1 == split_lines_ids[ith+1]:
        #         drop_iths.append(ith+1)

        # finall split idx, plus with final index before make pairwise
        new_split_ids = [0] + [idx for ith, idx in enumerate(split_lines_ids) if ith not in drop_iths] + [len(total_lines)]


        # segmentation
        segments_params = []
        for start_idx, end_idx in itertools.pairwise(new_split_ids):
            print(start_idx, end_idx)
            seg_params = {
                    "code_lines": total_lines[start_idx: end_idx],
                    "start_line": start_idx+1
                }
            segments_params.append(seg_params)

        return segments_params
    
    @staticmethod
    def check(file:str)->List[Dict[str,str]]:
        """
        Function to check indentation of python code
        Args:
            - file: system path (can be relative) for open and read
        """
        print('checker run: ',file)
        # get lines in file
        with open(file,'r') as fp:
            total_lines = fp.readlines()

        # segmentation
        segments_params = IndentChecker.file2entities(total_lines)
        
        # for seg in segments_params:
        #     print(seg)
        #     print('-----------------------------------\n')

        # find indent error in all lines
        segs_list = [Segment(**param) for param in segments_params]

        # for seg in segs_list:
        #     print(seg)

        # collect all errors
        total_errors = {}
        for seg in segs_list:
            total_errors.update(seg.get_error_dict())
        
        # print('in indent checker:',total_errors)
        return [{
            'line': line,
            'line_number': ith+1,
            'error': True if total_errors.get(ith+1) is not None else False
        }
        for ith, line in enumerate(total_lines)
        ]