#!/usr/bin/env python

# To be called from crontab:
# 5 7,15,21 * * * $HOME/.virtualenvs/<your venv>/bin/python $HOME/bin/pip_update.py
#
# Uses terminal-notifier 2.0 or above on macOS Sierra.
# To install terminal-notifer, use Homebrew: brew install terminal-notifier

from __future__ import print_function
import json
from subprocess import check_output, CalledProcessError, STDOUT
import argparse
import os
import sys
from importlib.metadata import distributions

try:
    from packaging.version import parse, InvalidVersion
    import requests
except ImportError as err:
    print(f"Please install {err.name}.")
    sys.exit(1)

PYPI_URL = 'https://pypi.org/pypi'
VERSION = '4.0.2'


def decode(string):
    """py2/3 compatibility"""
    return string if str is bytes else string.decode()


def notification(title='', subtitle='', message='', enable_actions=True):
    """ Uses terminal-notifier for showing notifications."""
    cmd = ['terminal-notifier', '-title', title,
           '-subtitle', subtitle, '-message', message,
           '-group', 'com.github.sashkab.pipupdate', ]
    if enable_actions:
        cmd.extend(['-actions', 'Update',])

    with open('/dev/null') as null:
        res = check_output(cmd, stdin=null)
        return decode(res).strip()


def get_version(package, url_pattern=PYPI_URL + '/{package}/json'):
    """Return version of package on pypi.python.org using json."""
    req = requests.get(url_pattern.format(package=package),
                       headers={'Accept':'application/json'})
    version = parse('0')
    if req.status_code == requests.codes.ok:
        j = json.loads(req.text)
        if 'releases' in j:
            releases = j['releases']
            for release in releases:
                try:
                    ver = parse(release)
                except InvalidVersion:
                    continue
                yanked = False
                release_info = j.get('releases', {}).get(release, [])
                if release_info:
                    yanked = release_info[0].get('yanked', False)
                if not ver.is_prerelease and not yanked:
                    version = max(version, ver)
    return version


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('-S', '--stdout', action='store_true', help="output to stdout")
    parser.add_argument('-M', '--markdown', action='store_true', help="output markdown to stdout")
    args = parser.parse_args()

    if args.markdown:
        pattern = '{dist.name} {dist.version} -> [{new_version}]({pypi}/{dist.name}/{new_version})'
        sep = '\n'
    elif args.stdout:
        pattern = "{dist.name}=={new_version}"
        sep = '\n'
    else:
        pattern = "{dist.name}"
        sep = ', '

    updates = []
    for dist in distributions():
        pypi_version = get_version(dist.name)
        installed_version = parse(dist.version)
        if not pypi_version.is_prerelease and pypi_version > installed_version:
            updates.append(pattern.format(dist=dist, new_version=str(pypi_version), pypi=PYPI_URL))

    if updates:
        if args.markdown or args.stdout:
            print(sep.join(updates))
        else:
            notification(title=f"pip: {len(updates)} updates", message=sep.join(updates),
                         enable_actions='PIP_NO_INDEX' not in os.environ)


if __name__ == '__main__':
    main()
