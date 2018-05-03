#!/usr/bin/python

from __future__ import print_function

from argparse import ArgumentParser, REMAINDER
from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from itertools import chain
import os.path
import sys

from jinja2 import Environment, FileSystemLoader
import ledger


def u8(x):
    return str(x).decode('utf-8')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--file', '-f', metavar='FILENAME',
                        help='ledger file')
    parser.add_argument('--output', '-o', metavar='FILENAME',
                        help='output file')
    parser.add_argument('--commodity',
                        help='graph only this commodity')
    parser.add_argument('query', nargs=REMAINDER, default='^assets',
                        help='base query to graph')
    return parser.parse_args()


@contextmanager
def file_or_std(arg, std):
    if arg:
        with open(arg, 'w') as f:
            yield f
    else:
        yield std


def main():
    args = parse_args()

    env = Environment(
        loader=FileSystemLoader(os.path.dirname(sys.argv[0])),
        autoescape=True)
    template = env.get_template('assets.html.j2')

    journal = ledger.read_journal(args.file)

    balances_by_date = dict()  # {date: {account: balance}}
    balances = dict()  # {account: balance}
    for post in journal.query('register %s' % ' '.join(
            arg for arg in args.query if arg != '--')):
        if (args.commodity
                and post.amount.commodity.symbol != args.commodity):
            continue
        account = u8(post.account.fullname())
        date = u8(post.xact.date)
        amount = post.amount.to_double()
        if date not in balances_by_date:
            balances_by_date[date] = deepcopy(balances)
        if account not in balances_by_date[date]:
            balances_by_date[date][account] = 0
        if account not in balances:
            balances[account] = 0
        balances_by_date[date][account] += amount
        balances[account] += amount

    with file_or_std(args.output, sys.stdout) as f:
        print(template.render(
                balances=sorted(list(balances_by_date.items())),
                keys=sorted(list(balances.keys()))).encode('utf-8'),
            file=f)


if __name__ == '__main__':
    sys.exit(main())
