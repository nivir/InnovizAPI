from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools
import pybind11

"""
file is build based on https://github.com/pybind/cmake_example.git example
"""

__version__ = '4.4.1'

package_name = 'innopy'

class get_pybind_include(object):
    """Helper class to determine the pybind11 include path

    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


ext_modules = [
    Extension(
        'api',
        ['src/main.cpp'],
        include_dirs=[
			'src/',
            'include/',
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True)
        ],
		libraries = ['innovizApi'],
		library_dirs=[package_name],
        language='c++'
    ),
]


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True
	
def assert_flag(compiler, flagname):
	if not has_flag(compiler, flagname):
		raise RuntimeError('Unsupported compiler -- %s flag is not supported' % flagname)
	
	return flagname


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.

    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')

class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        ct = self.compiler.compiler_type
        lopts = []
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')			
            lopts.append('-Wl,-rpath,$ORIGIN')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            #opts.append(assert_flag(self.compiler, '-Wl,-rpath,$ORIGIN'))		
            ext.extra_compile_args = opts
            ext.extra_link_args = lopts
        build_ext.build_extensions(self)

setup(
    name=package_name,
    version=__version__,
    author='Innoviz Technologies LTD',
    description='Innoviz API Python package',
    long_description='',
    platforms=["Windows", "Linux", "Unix"],
    ext_package=package_name,
    ext_modules=ext_modules,
    packages=[package_name],
    package_dir={package_name: package_name},
    package_data={package_name: ['innovizApi.dll', 'libinnovizApi.so', 'libpcap.so.1']},
    install_requires=[
    'pybind11>=2.2',
    'numpy>= 1.7.0'
    ],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)
