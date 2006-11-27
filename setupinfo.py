import sys, os
from setuptools.extension import Extension

try:
    from Pyrex.Distutils import build_ext as build_pyx
    PYREX_INSTALLED = True
except ImportError:
    PYREX_INSTALLED = False

EXT_MODULES = [
    ("etree",       "lxml.etree"),
    ("objectify",   "lxml.objectify")
    ]

def ext_modules(static_include_dirs, static_library_dirs, static_cflags): 
    if PYREX_INSTALLED:
        source_extension = ".pyx"
    else:
        print ("NOTE: Trying to build without Pyrex, pre-generated "
               "'src/lxml/etree.c' needs to be available.")
        source_extension = ".c"
    
    _include_dirs = include_dirs(static_include_dirs)
    _library_dirs = library_dirs(static_library_dirs)
    _cflags = cflags(static_cflags)
    _define_macros = define_macros()

    if OPTION_AUTO_RPATH:
        runtime_library_dirs = _library_dirs
    else:
        runtime_library_dirs = []
    
    result = []
    for module, package in EXT_MODULES:
        result.append(
            Extension(
            package,
            sources = ["src/lxml/" + module + source_extension],
            extra_compile_args = ['-w'] + _cflags,
            define_macros = _define_macros,
            include_dirs = _include_dirs,
            library_dirs = _library_dirs,
            runtime_library_dirs = runtime_library_dirs,
            libraries=['xslt', 'exslt', 'xml2', 'z', 'm'],
            ))
    return result

def extra_setup_args():
    result = {}
    if PYREX_INSTALLED:
        result['cmdclass'] = {'build_ext': build_pyx}
    return result

def library_dirs(static_library_dirs):
    if OPTION_STATIC:
        assert static_library_dirs, "Static build not configured, see doc/build.txt"
        return static_library_dirs
    # filter them from xslt-config --libs
    result = []
    possible_library_dirs = flags('xslt-config --libs')
    for possible_library_dir in possible_library_dirs:
        if possible_library_dir.startswith('-L'):
            result.append(possible_library_dir[2:])
    return result

def include_dirs(static_include_dirs):
    if OPTION_STATIC:
        assert static_include_dirs, "Static build not configured, see doc/build.txt"
        return static_include_dirs
    # filter them from xslt-config --cflags
    result = []
    possible_include_dirs = flags('xslt-config --cflags')
    for possible_include_dir in possible_include_dirs:
        if possible_include_dir.startswith('-I'):
            result.append(possible_include_dir[2:])
    return result

def cflags(static_cflags):
    result = []
    if OPTION_DEBUG_GCC:
        result.append('-g2')

    if OPTION_STATIC:
        assert static_cflags, "Static build not configured, see doc/build.txt"
        result.extend(static_cflags)
        return result

    # anything from xslt-config --cflags that doesn't start with -I
    possible_cflags = flags('xslt-config --cflags')
    for possible_cflag in possible_cflags:
        if not possible_cflag.startswith('-I'):
            result.append(possible_cflag)
    return result

def define_macros():
    if OPTION_WITHOUT_ASSERT:
        return [('PYREX_WITHOUT_ASSERTIONS', None)]
    return []
    
def flags(cmd):
    wf, rf, ef = os.popen3(cmd)
    return rf.read().split()

def has_option(name):
    try:
        sys.argv.remove('--%s' % name)
        return True
    except ValueError:
        return False

# pick up any commandline options
OPTION_WITHOUT_ASSERT = has_option('without-assert')
OPTION_STATIC = has_option('static')
OPTION_DEBUG_GCC = has_option('debug-gcc')
OPTION_AUTO_RPATH = has_option('auto-rpath')