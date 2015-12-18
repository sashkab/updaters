#!/usr/bin/env python

# To be called from crontab:
# 5 7,15,21 * * * $HOME/.virtualenvs/<your venv>/bin/python $HOME/bin/pip_update.py
#
# Uses terminal-notifier in OS X Mountain Lion and above. To install it use command:
# sudo gem install terminal-notifier

import pip
import requests
import json
from subprocess import call
import argparse

try:
    from packaging.version import parse
except ImportError:
    from pip._vendor.packaging.version import parse


def notification(title='', subtitle='', message=''):
    """ Uses terminal-notifier for showing notifications."""
    with open('/dev/null') as null:
        call(['terminal-notifier', '-title', title, '-subtitle', subtitle, '-message', message], stdin=null)


def get_version(package, url_pattern='https://pypi.python.org/pypi/{package}/json'):
    """Return version of package on pypi.python.org using json."""
    r = requests.get(url_pattern.format(package=package))
    v = parse('0.0')
    if r.status_code == requests.codes.ok:
        j = json.loads(r.text.encode(r.encoding))
        if 'releases' in j:
            rls = j['releases']
            for x in rls:
                v = max(v, parse(x))
    return v


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--stdout', action='store_true', help="Don't use notification, output to stdout")
    parser.add_argument('--markdown', action='store_true', help="Enable markdown output")
    args = parser.parse_args()
    new = []
    for dist in pip.get_installed_distributions():
        version = get_version(dist)  # TODO: Capitalize first letter (?)
        if not version.is_prerelease and version > parse(dist.version):
            if args.markdown:
                url = '{pypi}/{dist.project_name}/{ver}'.format(pypi=PYPI_URL, dist=dist, ver=available[0])
                new.append('{dist.project_name} {dist.version} -> [{available}]({url})'.format(dist=dist,
                                                    available=str(version), url=url))
            else:
                new.append('{dist.project_name} {dist.version} -> {available}'.format(dist=dist, available=str(version)))
    if new:
        if args.stdout:
            print('\n'.join(new))
        else:
            notification(title='pip updates', message='\n'.join(new))


if __name__ == '__main__':
    main()
