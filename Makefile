
.PHONY: docs

docs:
	mkdocs build
	pdoc -o output/api-docs --html simple_3dviz
	mv output/api-docs/simple_3dviz/* output/api-docs/
	rmdir output/api-docs/simple_3dviz
