all: assets.html expenses.html

assets.html: ../assets.py ../assets.html.j2 example.ledger
	../assets.py -f example.ledger -o $@

expenses.html: ../expenses.py ../expenses.html.j2 example.ledger
	../expenses.py -f example.ledger -o $@
