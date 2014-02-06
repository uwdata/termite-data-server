all: apps/infovis_mallet

apps/infovis_mallet:
	./demo.sh infovis mallet

clean:
	rm -rf externals/
	rm -rf tools/
	rm -rf apps/infovis_mallet
