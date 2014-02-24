#!/usr/bin/env python
# Adapted from http://code.activestate.com/recipes/577708-check-for-package-updates-on-pypi-works-best-in-pi/
# To be called from crontab:
# 5 7,15,21 * * * $HOME/.virtualenvs/<your venv>/bin/python $HOME/bin/pip_update.py
# Uses terminal-notifier in OS X Mountain Lion and above. To install it use command:
# sudo gem install terminal-notifier


import xmlrpclib
import pip
from subprocess import call
import argparse


def notification(title='', subtitle='', message=''):
    """ Uses terminal-notifier for showing notifications.

    """
    with open('/dev/null') as null:
	call(['terminal-notifier', '-title', title, '-subtitle', subtitle,'-message', message], stdin=null)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stdout', action='store_true', help="Don't use notification, output to stdout")
    args = parser.parse_args()

    new = []
    pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    for dist in pip.get_installed_distributions():
	available = pypi.package_releases(dist.project_name)
	if not available:  # Try to capitalize pkg name
	    available = pypi.package_releases(dist.project_name.capitalize())

	if available and available[0] != dist.version:
	    new.append('{dist.project_name} {dist.version} -> {available}'.format(dist=dist, available=available[0]))

    if new:
	if args.stdout:
	    print '\n'.join(new)
	else:
	    notification(title='pip updates', message='\n'.join(new))
