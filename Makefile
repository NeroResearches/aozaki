.PHONY: examples
examples:
	python3 -m aozaki examples/addition.ao
	python3 -m aozaki examples/callcc.ao
	python3 -m aozaki examples/church-numerals.ao
	python3 -m aozaki examples/option.ao
	python3 -m aozaki examples/omit_bind.ao
	python3 -m aozaki examples/cursed_identifiers.ao
	python3 -m aozaki examples/quicksort.ao

.DEFAULT_GOAL := examples
