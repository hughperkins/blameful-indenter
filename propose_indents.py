#!/usr/bin/python
"""
Copyright Hugh Perkins 2016

You can use this under the BSDv2 license

This script will re-indent files, creating new files with postfix '.proposed' added

You can then edit these (eg reindent files which have crazy insane auto-indentation :-P), and then
run commit_indents on them, to commit those indentation changes.  Make sure not to change the number of lines,
or move any lines around, since that will likely not create the final results that you want :-)

Note that you dont have to use this script: you can simply copy the old file to have suffix '.proposed', then
modify if by hand.  Depending on the source file, this might be quicker than running propose_indents.py first :-)

Usage:

  python propose_indents.py Abs.lua [file2.lua] [file3.lua] ...
"""

import sys
import os
from os import path
import subprocess


def get_num_lines(filepath):
  num_lines = int(subprocess.check_output([
    'wc', '-l', filepath
  ]).split()[0])
  return num_lines

def reindent(filepath, new_filepath, indentsize=2):
  original_num_lines = get_num_lines(filepath)

  f = open(filepath, 'r')
  contents = f.read()
  f.close()

  f = open(new_filepath, 'w')
  indent = 0
  indent = 0
  nextindent = 0
  line_num = 1
  last_line = None
  in_code_block = False
  block_indent = 0
  next_block_indent = 0
  if contents.endswith('\n'):
    contents = contents[:-1]
  for line in contents.split('\n'):
    original_line = line
    line = line.strip()
    prefix = ''
    if not in_code_block:
      comment_pos = line.find('--')
      if comment_pos >= 0:
        pc = line[:comment_pos]
        comments = line[comment_pos:]
      else:
        pc = line
        comments = ''
      if '[[' in pc:
        codeblock_pos = pc.find('[[')
        pc = pc[:codeblock_pos]
        comments = pc[codeblock_pos:]
        in_code_block = True
        block_indent = 0
        next_block_indent = 1
    if in_code_block:
      if ']]' in line:
        codeblock_end = line.find(']]') + 2
        prefix = line[:codeblock_end]
        pc = line[codeblock_end:]
        in_code_block = False
        comments = ''
      else:
        pc = ''
        comments = line
        if(comments.startswith('if') or comments.startswith('for ') or comments.startswith('while') or comments.startswith('function')
            or comments.startswith('local function') or comments.find(' = function(') >= 0):
          next_block_indent += 1
        elif comments.startswith('elseif') or comments.startswith('else'):
          block_indent -= 1
        if comments.startswith('end') or comments.endswith('end'):
          block_indent -= 1
        indent += block_indent
        block_indent = next_block_indent
    pcs = pc.strip()
    if(pcs.startswith('if') or pcs.endswith(' do') or pcs == 'do' or pcs.startswith('function')
        or pcs.startswith('local function') or pcs.find(' function(') >= 0 or pcs.find('=function(') >= 0):
      nextindent += 1
    elif pcs.startswith('elseif') or pcs.startswith('else'):
      indent -= 1
    if pcs.startswith('end') or pcs.endswith('end'):
      indent -= 1
      nextindent -= 1
    # handle brackets...
    excess_brackets = pc.count('(') + pc.count('{') - pc.count(')') - pc.count('}')
    nextindent += excess_brackets
    if excess_brackets < 0 and (pc[0] == ')' or pc[0] == '}'):
      indent = nextindent
#    if line_num in lines:
    f.write(' ' * (indentsize * indent) + prefix + pc + comments + '\n')
    indent = nextindent
    last_line = line
    line_num = line_num + 1
  f.close()
  new_num_lines = get_num_lines(filepath)
  if new_num_lines != original_num_lines:
    raise Exception('number of lines dont match ', filepath)

def process_file(filename, proposed_file):
  subprocess.check_output([
    'git', 'checkout', filename
  ])
  reindent(filename, proposed_file)

if __name__ == '__main__':
  filenames=sys.argv[1:]
  for filename in filenames:
    if filename.endswith('.proposed'):
      continue
    print('  ' + filename)
    process_file(filename, filename + '.proposed')
  print('Proposed files written.  Please check them, then run commit_indents.py, to commit your changes')

