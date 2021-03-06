import Options
from os import unlink, symlink
from os.path import exists, abspath
import os

srcdir = '.'
blddir = 'build'
ncursesdir = abspath(srcdir) + "/deps/ncurses"
VERSION = '0.0.1'

def set_options(opt):
  opt.tool_options('compiler_cxx')

def configure(conf):
  conf.check_tool('compiler_cxx')
  conf.check_tool('node_addon')
  
  # ugly hack to append -fPIC for x64
  hack = ""
  if (conf.env['DEST_CPU'] == 'x86_64'):
    hack = "sed -i 's/^CFLAGS_NORMAL.*$/CFLAGS_NORMAL\t= $(CCFLAGS) -fPIC/' " + ncursesdir + "/c++/Makefile && sed -i 's/^CFLAGS_NORMAL.*$/CFLAGS_NORMAL\t= $(CCFLAGS) -fPIC/' " + ncursesdir + "/ncurses/Makefile && sed -i 's/^CFLAGS_NORMAL.*$/CFLAGS_NORMAL\t= $(CCFLAGS) -fPIC/' " + ncursesdir + "/panel/Makefile"

  # configure ncurses
  print "Configuring ncurses library ..."
  cmd = "cd deps/ncurses && ./configure --without-debug"
  if os.system(cmd) != 0:
    conf.fatal("Configuring ncurses failed.")
  else:
    os.system(hack)

def build(bld):
  print "Building ncurses library ..."
  cmd = "cd deps/ncurses && make"
  if os.system(cmd) != 0:
    conf.fatal("Building ncurses failed.")
  else:
    obj = bld.new_task_gen('cxx', 'shlib', 'node_addon')
    obj.target = 'ncurses'
    obj.source = 'ncurses.cc'
    obj.includes = [ncursesdir + '/include', ncursesdir + '/c++']
    obj.cxxflags = ['-O2']
    obj.linkflags = [ncursesdir + '/lib/libncurses++.a', ncursesdir + '/lib/libpanel.a', ncursesdir + '/lib/libncurses.a']

def shutdown():
  # HACK to get ncurses.node out of build directory.
  # better way to do this?
  if Options.commands['clean']:
    if exists('ncurses.node'): unlink('ncurses.node')
  else:
    if exists('build/default/ncurses.node') and not exists('ncurses.node'):
      symlink('build/default/ncurses.node', 'ncurses.node')
