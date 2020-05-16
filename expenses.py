#!/usr/bin/python3

from argparse import ArgumentParser, REMAINDER
from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
import os.path
import sys

from jinja2 import Environment, FileSystemLoader
import ledger


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--file', '-f', metavar='FILENAME',
                        required=True, help='ledger file')
    parser.add_argument('--output', '-o', metavar='FILENAME',
                        help='output file')
    parser.add_argument('--commodity',
                        help='graph only this commodity')
    parser.add_argument('query', nargs=REMAINDER,
                        help='query to graph')
    args = parser.parse_args()

    if args.query and args.query[0] == '--':
        del args.query[0]
    args.query = ' '.join(['register'] + (args.query or ['^Expenses']))

    return args


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
    template = env.get_template('expenses.html.j2')

    journal = ledger.read_journal(args.file)

    balances_by_month = dict()  # {month: {account: balance}}
    accounts = set()
    for post in journal.query(args.query):
        if (args.commodity
                and post.amount.commodity.symbol != args.commodity):
            continue
        account = post.account.fullname()
        month = '%04d-%02d' % (
            post.xact.date.year, post.xact.date.month)
        payee = post.xact.payee
        amount = post.amount.to_double()
        accounts.add(account)
        if month not in balances_by_month:
            balances_by_month[month] = dict()
        if account not in balances_by_month[month]:
            balances_by_month[month][account] = 0
        balances_by_month[month][account] += amount

    with file_or_std(args.output, sys.stdout) as f:
        print(template.render(
                balances=sorted(list(balances_by_month.items())),
                keys=sorted(list(accounts))),
            file=f)


if __name__ == '__main__':
    sys.exit(main())
