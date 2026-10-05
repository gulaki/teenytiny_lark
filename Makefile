.PHONY: test demo clean

test:
	python -m pytest

demo:
	python -m teenytiny.cli examples/fibonacci.teeny -o build/fibonacci.c --build make --build-output build/Makefile

clean:
	rm -rf build/*.c build/Makefile build/*.ninja build/fibonacci
