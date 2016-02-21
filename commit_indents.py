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

def copy_lines(filename, proposed_file, lines):
  # use lines from filename, except for lines specified in lines, which will come
  # from proposed_file
  f = open(filename, 'r')
  old_lines = f.read().split('\n')
  f.close
  f = open(proposed_file, 'r')
  proposed_lines = f.read().split('\n')
  f.close

  num_lines = get_num_lines(filename)
  new_num_lines = get_num_lines(proposed_file)
  assert(num_lines == new_num_lines, 'files should have same number of lines, but not the case for ' + filename)
  of = open(filename, 'w')
  for i in range(num_lines):
    line_num = i + 1
    if line_num in lines:
      of.write(proposed_lines[i] + '\n')
    else:
      of.write(old_lines[i] + '\n')
  of.close()

def write_out_changes(proposed_file_suffix):
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
      print('filename', filename)
      print('lines', lines)
      copy_lines(filename, filename + proposed_file_suffix, lines)
#    os.exit(1)
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
  write_out_changes('.proposed')
  print('All done')

