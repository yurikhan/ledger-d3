#!/usr/bin/python3

from argparse import ArgumentParser, REMAINDER
from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from itertools import chain
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
    parser.add_argument('--commodity', required=True,
                        help='normalize all amounts to this commodity')
    parser.add_argument('query', nargs=REMAINDER,
                        help='base query to graph')
    args = parser.parse_args()

    if args.query and args.query[0] == '--':
        del args.query[0]
    args.query = ' '.join(['register'] + (args.query or ['^Assets']))

    return args


@contextmanager
def file_or_std(arg, std):
    if arg:
        with open(arg, 'w') as f:
            yield f
    else:
        yield std


def amount_sum(date, base_commodity, amounts):
    result = None
    for amount in amounts:
        value = amount.value(base_commodity, date)
        result = value if result is None else result + value
    return result.to_double() if result is not None else 0


def main():
    args = parse_args()

    env = Environment(
        loader=FileSystemLoader(os.path.dirname(sys.argv[0])),
        autoescape=True)
    template = env.get_template('assets.html.j2')

    journal = ledger.read_journal(args.file)

    balances_by_date = {}  # type: Dict[date, Dict[AccountName, Dict[CommodityName, float]]]
    last_date = None
    balances = {}  # type: Dict[AccountName, Dict[CommodityName, float]]
    for post in sorted(journal.query(args.query),
                       key=lambda p: p.xact.date):
        date = post.xact.date
        account = post.account.fullname()
        commodity = post.amount.commodity.symbol
        amount = post.amount.to_double()

        if date != last_date:
            if last_date is not None:
                balances_by_date[last_date] = deepcopy(balances)
            last_date = date
        if account not in balances:
            balances[account] = {}  # type: Dict[CommodityName, float]
        if commodity not in balances[account]:
            balances[account][commodity] = 0
        balances[account][commodity] += amount
    balances_by_date[last_date] = deepcopy(balances)

    base_commodity = ledger.commodities.find(args.commodity)
    worth_by_date = {
        date: {
            account: amount_sum(date, base_commodity,
                (ledger.Amount('{:f}'.format(amount))
                       .with_commodity(ledger.commodities.find(commodity))
                 for commodity, amount in commodity_balances.items()))
            for account, commodity_balances in balances.items()}
        for date, balances in balances_by_date.items()}

    with file_or_std(args.output, sys.stdout) as f:
        print(template.render(
                balances=sorted(list(worth_by_date.items())),
                keys=sorted(list(balances.keys()))),
            file=f)


if __name__ == '__main__':
    sys.exit(main())
