.PHONY: build

TMPDIR := $(shell mktemp -d)

tempdir:
	@rm -rf $(TMPDIR)

build: tempdir
	virtualenv -p python3 $(TMPDIR)
	. $(TMPDIR)/bin/activate && pip install -r requirements.txt
	$(TMPDIR)/bin/pyinstaller --noconfirm --onefile --clean --noupx cqlsh.py -n cqlsh
	rm -rf $(TMPDIR)