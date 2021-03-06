#!/usr/bin/python
"""
Copyright Hugh Perkins 2016

You can use this under the BSDv2 license

This script re-indent files, without changing git blame.  It will create
a new commit for each author present in the original blame, with commit message
'automated re-indentation'

Usage:

  python change_indent.py Abs.lua

You can put multiple files, and changes will be grouped by author, across *all* provided files, so
that there will be one commit per author (rather than one commit per author per file...)

  python change_indent.py *.lua

"""

import sys
import os
from os import path
import subprocess


lines_by_file_by_author = {}
author_info_by_email = {}

def get_num_lines(filepath):
  num_lines = int(subprocess.check_output([
    'wc', '-l', filepath
  ]).split()[0])
  return num_lines

def reindent(filepath, lines, indentsize=3):
  original_num_lines = get_num_lines(filepath)
#  print('original_num_lines', original_num_lines)

  f = open(filepath, 'r')
  contents = f.read()
  f.close()

  f = open(filepath, 'w')
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
    if line_num in lines:
#      print(line_num, 'writing modified line [', original_line, ']')
      final_line = ' ' * (indentsize * indent) + prefix + pc + comments
      if final_line.strip() == '':  # dont want trailing spaces probably
        f.write('\n')
      else:
        f.write(final_line + '\n')
    else:
#      print(line_num, 'writing original line [', original_line, ']')
      f.write(original_line + '\n')
    indent = nextindent
    last_line = line
    line_num = line_num + 1
#  if last_line != '':
#    f.write('\n')
  f.close()
  new_num_lines = get_num_lines(filepath)
#  print('new_num_lines', new_num_lines, 'before', original_num_lines)
  if new_num_lines != original_num_lines:
    raise Exception('number of lines dont match ', filepath)

def process_line_info(filename, line_info):
#  print(line_info)
  author_email = line_info['author-mail']
  if author_email not in author_info_by_email:
    author_info = {}
    author_info['email'] = author_email
    author_info['name'] = line_info['author']
    author_info_by_email[author_email] = author_info
  line_num = line_info['line_num']
  if author_email not in lines_by_file_by_author:
    lines_by_file_by_author[author_email] = {}
  lines_by_file = lines_by_file_by_author[author_email]
  if filename not in lines_by_file:
    lines_by_file[filename] = []
  lines = lines_by_file[filename]
  lines.append(line_num)

def process_file(filename):
  subprocess.check_output([
    'git', 'checkout', filename
  ])
  out = subprocess.check_output([
    'git', 'blame', '--line-porcelain', filename
  ])
  #print('out', out)

  line_num = 0  # 1-based, otherwise inconsistent with all of: lua, text editors, and git blame output
  line_info = {}
  #in_boundary = False
  #boundary_line = -1
  for line in out.split('\n'):
#    print('processing line [' + line + ']')
    key = line.split(' ')[0]
#    print('key', key)
    if len(key) > 39 and key[0] != '\t':
      if len(line_info.keys()) > 0:
        process_line_info(filename, line_info)

      in_boundary = False
      line_num = line_num + 1
      line_info = {}
      line_info['line_num'] = line_num
      continue
  #  if in_boundary:
  #    if boundary_line == 2:
  #      line_info['contents'] = line.rstrip()[1:]
  #    boundary_line = boundary_line + 1
  #  else:
  #    if key == 'boundary':
  #      in_boundary = True
  #      boundary_line = 1
  #    else:
    if key is not None and key != '' and len(key) < 40:
      value = line.strip().replace(key + ' ', '')
      if value.strip() != '':
        if key in ['author', 'author-mail', 'summary']:
          if key == 'author-mail':
            value = value.replace('.(none)', '')  # for pc-wolf###.(none)
          line_info[key] = value
    elif len(key) > 1 and key[0] == '\t':
      line_info['contents'] = line.rstrip()[1:]
  if len(line_info.keys()) > 0:
    process_line_info(filename, line_info)

#  print(lines_by_file_by_author)

def write_out_changes():
  for author_email, lines_by_file in lines_by_file_by_author.iteritems():
    author_info = author_info_by_email[author_email]
    print('  ' + author_info['name'])
    subprocess.call([
      'git', 'config', '--local', '--unset', 'user.name'
    ])
    subprocess.call([
      'git', 'config', '--local', '--unset', 'user.email'
    ])
    subprocess.check_output([
      'git', 'config', '--local', '--add', 'user.name', author_info['name']
    ])
    subprocess.check_output([
      'git', 'config', '--local', '--add', 'user.email', author_email
    ])
#    subprocess.check_output([
#      'git', 'config', '--local', '-l'
#    ])
    for filename, lines in lines_by_file.iteritems():
      reindent(filename, lines)
    diffs = subprocess.check_output([
      'git', 'diff'
    ])
#    print('diffs[' + diffs + ']')
    if diffs != '':
      subprocess.check_output([
        'git', 'add', '-u'
      ])
      subprocess.check_output([
        'git', 'commit', '-m', 'automated re-indentations for changes by ' + author_info['name']
      ])
    else:
      print('    no changes => skipping')
    subprocess.call([
      'git', 'config', '--local', '--unset', 'user.name'
    ])
    subprocess.call([
      'git', 'config', '--local', '--unset', 'user.email'
    ])

if __name__ == '__main__':
  filenames=sys.argv[1:]
  # we need to:
  # - first extract all authors, get line info
  # - write out all files for all authors
  print('Reading blames from files:')
  for filename in filenames:
    print('  ' + filename)
    process_file(filename)
  print('Writing out changes:')
  write_out_changes()
  print('All done')

