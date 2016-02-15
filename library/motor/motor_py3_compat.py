# Copyright 2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals, absolute_import

"""Python 2.6+ compatibility utilities for Motor."""

import sys

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True

if PY3:
    string_types = str,
    integer_types = int,
    text_type = str
    from io import BytesIO as StringIO
else:
    string_types = basestring,
    integer_types = (int, long)
    text_type = unicode

    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO


def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass.

    Copied from "six".
    """
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper
