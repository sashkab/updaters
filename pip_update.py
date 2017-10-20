#!/usr/bin/env python

# To be called from crontab:
# 5 7,15,21 * * * $HOME/.virtualenvs/<your venv>/bin/python $HOME/bin/pip_update.py
#
# Uses terminal-notifier 1.7 or above on macOS Sierra.
# To install terminal-notifer, use Homebrew: brew install terminal-notifier

from __future__ import print_function
import json
from subprocess import check_output, CalledProcessError, STDOUT
import argparse
from time import sleep
import os
import sys

try:
    import pkg_resources
    from packaging.version import parse
    import requests
except ImportError as err:
    print("Please install %s." % err.name)
    sys.exit(1)

PYPI_URL = 'https://pypi.python.org/pypi'
VERSION = '3.1'


def decode(string):
    """py2/3 compatibility"""
    return string if str is bytes else string.decode()


def notification(title='', subtitle='', message='', enable_actions=True):
    """ Uses terminal-notifier for showing notifications."""
    cmd = ['terminal-notifier', '-title', title,
           '-subtitle', subtitle, '-message', message,
           '-group', 'com.github.sashkab.pipupdate',
           '-json', ]
    if enable_actions:
        cmd.extend(['-actions', 'Update',])

    with open('/dev/null') as null:
        res = check_output(cmd, stdin=null)
        return decode(res).strip()


def get_version(package, url_pattern=PYPI_URL + '/{package}/json'):
    """Return version of package on pypi.python.org using json."""
    req = requests.get(url_pattern.format(package=package))
    version = parse('0')
    if req.status_code == requests.codes.ok:
        j = json.loads(req.text.encode(req.encoding).decode('utf8'))
        if 'releases' in j:
            releases = j['releases']
            for release in releases:
                ver = parse(release)
                if not ver.is_prerelease:
                    version = max(version, ver)
    return version


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION)
    parser.add_argument('-S', '--stdout', action='store_true', help="output to stdout")
    parser.add_argument('-M', '--markdown', action='store_true', help="output markdown to stdout")
    args = parser.parse_args()

    if args.markdown:
        pattern = '{dist.project_name} {dist.version} -> [{new_version}]({pypi}/{dist.project_name}/{new_version})'
        sep = '\n'
    elif args.stdout:
        pattern = "{dist.project_name}=={new_version}"
        sep = '\n'
    else:
        pattern = "{dist.project_name}"
        sep = ', '

    updates = []
    for dist in pkg_resources.working_set:
        pypi_version = get_version(dist.project_name)
        installed_version = parse(dist.parsed_version.base_version)
        if not pypi_version.is_prerelease and pypi_version > installed_version:
            updates.append(pattern.format(dist=dist, new_version=str(pypi_version), pypi=PYPI_URL))

    if updates:
        if args.markdown or args.stdout:
            print(sep.join(updates))
        else:
            action = notification(title="pip: %d updates" % len(updates), message=sep.join(updates),
                                  enable_actions='PIP_NO_INDEX' not in os.environ)
            try:
                js = json.loads(action)
            except json.decoder.JSONDecodeError:
                pass
            else:
                if js['activationType'] == 'actionClicked' and js['activationValue'] == 'Update':
                    cmd = ['pip', 'install', '-U'] + updates
                    try:
                        _ = check_output(cmd, stderr=STDOUT)
                    except CalledProcessError as err:
                        print("{err}\n{err.output}".format(err=err))


if __name__ == '__main__':
    main()
