#!/usr/bin/env python

# To be called from crontab:
# 5 7,15,21 * * * $HOME/.virtualenvs/<your venv>/bin/python $HOME/bin/pip_update.py
#
# Uses terminal-notifier 1.7 or above on macOS Sierra. 
# To install terminal-notifer, use Homebrew: brew install terminal-notifier

from __future__ import print_function
import pip
import requests
import json
from subprocess import check_output
import argparse
from time import sleep

from pip._vendor.packaging.version import parse

PYPI_URL = 'https://pypi.python.org/pypi'
VERSION = '2.2'

def notification(title='', subtitle='', message=''):
    """ Uses terminal-notifier for showing notifications."""
    with open('/dev/null') as null:
        r = check_output(['terminal-notifier', '-title', title, 
                          '-subtitle', subtitle, '-message', message,
                          '-dropdownLabel', 'Close', '-actions', 'Close,Install Updates',
                        ], stdin=null)
        return r.strip()


def get_version(package, url_pattern=PYPI_URL + '/{package}/json'):
    """Return version of package on pypi.python.org using json."""
    req = requests.get(url_pattern.format(package=package))
    v = parse('0')
    if req.status_code == requests.codes.ok:
        j = json.loads(req.text.encode(req.encoding).decode('utf8'))
        if 'releases' in j:
            releases = j['releases']
            for release in releases:
                ver = parse(release)
                if not ver.is_prerelease:
                    v = max(v, ver)
    return v


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION)
    parser.add_argument('-S', '--stdout', action='store_true', help="Don't use notification, output to stdout")
    parser.add_argument('-M', '--markdown', action='store_true', help="Enable markdown output")
    args = parser.parse_args()

    updates = {}
    for dist in pip.get_installed_distributions():
        pypi_version = get_version(dist.project_name)
        if not pypi_version.is_prerelease and pypi_version > dist.parsed_version:
            new_version = str(pypi_version)
            url = '{pypi}/{dist.project_name}/{ver}'.format(pypi=PYPI_URL, dist=dist, ver=new_version)
            if args.markdown:
                updates[dist.project_name]  = '{dist.project_name} {dist.version} -> [{n}]({u})'.format(dist=dist, n=new_version, u=url)
            else:
                updates[dist.project_name] = '{dist.project_name} {dist.version} -> {n}'.format(dist=dist, n=new_version)
        sleep(1)

    if updates:
        if args.markdown or args.stdout:
            print('\n'.join(updates.values()))
        else:
            action = notification(title='pip updates', message='\n'.join(updates.values()))
            if action.startswith("Install Updates"):
                check_output(['pip', 'install', '-U'] + updates.keys())


if __name__ == '__main__':
    main()

