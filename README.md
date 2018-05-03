# ledger-d3

Scripts to generate D3-based asset and expense graphs.


# Usage

```
$ assets.py -f 2018.ledger [-o assets.html] [--commodity USD] [^Assets]
$ expenses.py -f 2018.ledger [-o expenses.html] [--commodity USD] [^Expenses]
```

The `--file` (`-f`) option specifies a ledger data file.
`--output` (`-o`) specifies an output file; by default, it goes to standard output.
`--commodity` lets you choose a currency if your ledger uses more than one.
(NOTE: any postings in other currencies are skipped!)

Any other command line arguments are passed to a `ledger register` query;
see Ledger documentation for possible options.

You will probably want to limit the `expenses.py` query
to a date range excluding the opening balances.


# Dependencies

```
$ sudo apt-get install python-ledger python-jinja2
```

Windows and Mac users please figure out the environment for yourselves.
