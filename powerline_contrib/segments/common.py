from __future__ import unicode_literals, division, absolute_import, print_function

from powerline.segments import Segment, with_docstring
from powerline.theme import requires_segment_info, requires_filesystem_watcher

import subprocess
import tempfile
import os
import stat

@requires_segment_info
def environment(pl, segment_info, variable=None, contents=None):
	'''
	Return the value of any defined environment variable\n
	This is a modified version of
	:func:`powerline.segments.common.env.environment`.
	Useful for checking the existance of a variable
	without displaying its contents.\n
	:param variable: The environment variable to return if found
	:type variable: string
	:param contents: The variable value will be overridden by this if set
	:type contents: string, optional
	'''
	var = segment_info['environ'].get(variable, None)
	if var is None: return None
	if contents is None: return var
	return contents

@requires_filesystem_watcher
@requires_segment_info
def python(pl, segment_info, create_watcher, code=None):
	'''
	Return a value set by an arbitrary python block\n
	The resulting value should be stored in a variable named ``result``.\n
	:param code: A Python code block to be passed to :func:`exec`
	:type code: string
	'''
	scope = {'pl': pl,
		'segment_info': segment_info,
		'create_watcher': create_watcher}
	exec(code, None, scope)
	return scope.get('result', None)

@requires_segment_info
def shell(pl, segment_info, code=None):
	'''
	Return the stdout of an arbitrary executable\n
	:param code: An executable passed to be executed by the system
	:type code: string
	'''
	try:
		with tempfile.NamedTemporaryFile(mode='w', delete=False) as file:
			file.write(code)
		os.chmod(file.name, os.stat(file.name).st_mode | stat.S_IEXEC)
		return subprocess.run([file.name], check=True, capture_output=True).stdout
	finally:
		try: os.unlink(file.name)
		except: pass

@requires_filesystem_watcher
@requires_segment_info
def colored(pl, segment_info, create_watcher, code=None, highlight=None):
	'''
	Return a value set by an arbitrary python block colored by ``client_id``\n
	Similar to :func:`powerline_contrib.segments.common.python`,
	but the background color is semi-randomized based on ``client_id``.\n
	:param code: A Python code block to be passed to ``exec``
	:type code: string
	:param highlight: Names of highlight groups to be used
	:type highlight: list, optional
	'''
	return [{
		'contents': python(pl, segment_info, create_watcher, code),
		'highlight_groups': highlight or ['colored_gradient'],
		'gradient_level': ((150 + 12500**0.5) *
			segment_info.get('client_id', 0)) % 100,
	}]

