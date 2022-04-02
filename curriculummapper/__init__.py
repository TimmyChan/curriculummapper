#!python3

from .curriculummapper import Course, Curriculum

__all__ = ['Course', 'Curriculum']
'''The __init__.py files are required to make Python treat directories
containing the file as packages. This prevents directories with a common name,
such as string, unintentionally hiding valid modules that occur later on the
module search path. In the simplest case, __init__.py can just be an empty file
but it can also execute initialization code for the package
'''
'''
: if a package’s __init__.py code defines a list named __all__, it is taken to
 be the list of module names that should be imported when from package import *
 is encountered. It is up to the package author to keep this list up-to-date
 when a new version of the package is released. Package authors may also decide
 not to support it, if they don’t see a use for importing * from their package.
'''
