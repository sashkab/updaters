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
import os

from pip._vendor.packaging.version import parse

PYPI_URL = 'https://pypi.python.org/pypi'
VERSION = '2.2.15'


def decode(x):
    return x if str is bytes else x.decode()


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
            if args.markdown:
                url = '{pypi}/{dist.project_name}/{ver}'.format(pypi=PYPI_URL, dist=dist, ver=new_version)
                updates[dist.project_name]  = '{dist.project_name} {dist.version} -> [{n}]({u})'.format(dist=dist, n=new_version, u=url)
            else:
                updates[dist.project_name] = '{dist.project_name} {dist.version} -> {n}'.format(dist=dist, n=new_version)
        # sleep(1)

    if updates:
        if args.markdown or args.stdout:
            print('\n'.join(updates.values()))
        else:
            action = notification(title='pip updates', message=' '.join(updates.values()),
                                  enable_actions='PIP_NO_INDEX' not in os.environ)
            try:
                js = json.loads(action)
            except json.decoder.JSONDecodeError:
                pass
            else:
                if js['activationType'] == 'actionClicked' and js['activationValue'] == 'Update':
                    cmd = ['pip', 'install', '-U'] + list(updates.keys())
                    out = check_output(cmd)


if __name__ == '__main__':
    main()
