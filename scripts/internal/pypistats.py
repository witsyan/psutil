#!/usr/bin/env python3

# Copyright (c) 2009 Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Print PYPI statistics in MarkDown format.
Requires
"""

import datetime
import json
import os
import subprocess
import textwrap

import pypinfo  # NOQA

from psutil._common import memoize


AUTH_FILE = os.path.expanduser("~/.pypinfo.json")
PKGNAME = 'psutil'
DAYS = 30
LIMIT = 100
GITHUB_SCRIPT_URL = "https://github.com/giampaolo/psutil/blob/master/" \
                    "scripts/internal/pypistats.py"


@memoize
def sh(cmd):
    env = os.environ.copy()
    env['GOOGLE_APPLICATION_CREDENTIALS'] = AUTH_FILE
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise RuntimeError(stderr)
    assert not stderr, stderr
    return stdout.strip()


def top_packages():
    out = sh(f"pypinfo --all --json --days {DAYS} --limit {LIMIT} '' project")
    data = json.loads(out)
    return data


def ranking():
    data = top_packages()
    for i, line in enumerate(data['rows'], 1):
        if line['project'] == PKGNAME:
            return i
    raise ValueError(f"can't find {PKGNAME}")


def downloads():
    data = top_packages()
    for line in data['rows']:
        if line['project'] == PKGNAME:
            return line['download_count']
    raise ValueError(f"can't find {PKGNAME}")


def downloads_pyver():
    out = sh(f"pypinfo --json --days {DAYS} {PKGNAME} pyversion")
    return json.loads(out)


def downloads_by_country():
    out = sh(f"pypinfo --json --days {DAYS} {PKGNAME} country")
    return json.loads(out)


def downloads_by_system():
    out = sh(f"pypinfo --json --days {DAYS} {PKGNAME} system")
    return json.loads(out)


def downloads_by_distro():
    out = sh(f"pypinfo --json --days {DAYS} {PKGNAME} distro")
    return json.loads(out)


def print_markdown_table(title, left, rows):
    pleft = left.replace('_', ' ').capitalize()
    s = textwrap.dedent(f"""\
        ### {title}

        | {pleft} | Downloads      |
        |:--------|---------------:|\
        """)
    print(s)
    for row in rows:
        lval = row[left]
        rval = '{0:,}'.format(row['download_count'])
        print(f"| {lval} | {rval} |")
    print()


def print_markdown():
    last_update = datetime.datetime.now().strftime("%Y-%m-%d")
    s = textwrap.dedent(f"""\
        # Download stats

        psutil download statistics of the last {DAYS} days (last update
        *{last_update}*).
        Generated via [pypistats.py]({GITHUB_SCRIPT_URL}) script.
        """)
    print(s)

    per_month = '{0:,}'.format(downloads())
    per_day = '{0:,}'.format(int(downloads() / 30))
    s = textwrap.dedent(f"""\
        ### Overview

        |                           | Downloads        |
        |:--------------------------|-----------------:|
        | **Per month**             |      {per_month} |
        | **Per day**               |        {per_day} |
        | **PYPI ranking**          |      {ranking()} |

        *See more [details](https://pepy.tech/project/psutil).*
        """)
    print(s)

    print_markdown_table('Operating systems', 'system_name',
                         downloads_by_system()['rows'])

    print_markdown_table('Distros', 'distro_name',
                         downloads_by_distro()['rows'])

    print_markdown_table('Python versions', 'python_version',
                         downloads_pyver()['rows'])

    print_markdown_table('Countries', 'country',
                         downloads_by_country()['rows'])


def main():
    print_markdown()


main()
