#!/usr/bin/env python
# Adapted from http://code.activestate.com/recipes/577708-check-for-package-updates-on-pypi-works-best-in-pi/
# To be called from crontab:
# 5 7,15,21 * * * $HOME/.virtualenvs/<your venv>/bin/python $HOME/bin/pip_update.py

import xmlrpclib
import pip
from subprocess import call


def notification(title='', subtitle='', message=''):
    """ Uses terminal-notifier for showing notifications.

    """
    with open('/dev/null') as null:
	call(['terminal-notifier', '-title', title, '-subtitle', subtitle,'-message', message], stdin=null)


if __name__ == '__main__':
    new = []
    pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    for dist in pip.get_installed_distributions():
	available = pypi.package_releases(dist.project_name)
	if not available:  # Try to capitalize pkg name
	    available = pypi.package_releases(dist.project_name.capitalize())

	if available[0] != dist.version:
	    new.append('{dist.project_name} {dist.version} -> {available}'.format(dist=dist, available=available[0]))

    if new:
	notification(title='pip updates', message='\n'.join(new))
