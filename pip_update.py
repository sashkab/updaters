#!/usr/bin/env python
# Adapted from http://code.activestate.com/recipes/577708-check-for-package-updates-on-pypi-works-best-in-pi/
# To be called from crontab:
# 5 7,15,21 * * * $HOME/.virtualenvs/<your venv>/bin/python $HOME/bin/pip_update.py
# Uses terminal-notifier in OS X Mountain Lion and above. To install it use command:
# sudo gem install terminal-notifier


import xmlrpclib
import pip

try:
    from packaging.version import parse
except ImportError:
    from pip._vendor.packaging.version import parse

from subprocess import call
import argparse

PYPI_URL = 'http://pypi.python.org/pypi'


def notification(title='', subtitle='', message=''):
    """ Uses terminal-notifier for showing notifications."""
    with open('/dev/null') as null:
        call(['terminal-notifier', '-title', title, '-subtitle', subtitle, '-message', message], stdin=null)


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--stdout', action='store_true', help="Don't use notification, output to stdout")
    parser.add_argument('--markdown', action='store_true', help="Enable markdown output")
    args = parser.parse_args()

    new = []
    pypi = xmlrpclib.ServerProxy(PYPI_URL)
    for dist in pip.get_installed_distributions():
        available = pypi.package_releases(dist.project_name)
        if not available:  # Try to capitalize pkg name
            available = pypi.package_releases(dist.project_name.capitalize())

        if available:
            version = parse(available[0])
            dist_version = parse(dist.version)
            if not version.is_prerelease and version > dist_version:
                if args.markdown:
                    url = '{pypi}/{dist.project_name}/{ver}'.format(pypi=PYPI_URL, dist=dist, ver=available[0])
                    new.append('{dist.project_name} {dist.version} -> [{available}]({url})'.format(dist=dist,
                                                           available=version,
                                                           url=url))
                else:
                    new.append('{dist.project_name} {dist.version} -> {available}'.format(dist=dist, available=version))
    if new and args.stdout:
        print('\n'.join(new))
    elif new:
        notification(title='pip updates', message='\n'.join(new))


if __name__ == '__main__':
    main()
