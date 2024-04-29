.PHONY: examples
examples:
	python3 -m aozaki examples/addition.ao
	python3 -m aozaki examples/callcc.ao
	python3 -m aozaki examples/church-numerals.ao
	python3 -m aozaki examples/option.ao

.DEFAULT_GOAL := examples
