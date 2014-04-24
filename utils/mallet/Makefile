all: CorpusWriter.jar

lib:
	mkdir lib
	ln -s ../../../tools/mallet/dist/mallet.jar lib/mallet.jar
	ln -s ../../../tools/mallet/dist/mallet-deps.jar lib/mallet-deps.jar

mallet_helpers/CorpusWriter.class: lib mallet_helpers/CorpusWriter.java
	javac -cp .:lib/mallet.jar:lib/mallet-deps.jar mallet_helpers/CorpusWriter.java

CorpusWriter.jar: mallet_helpers/CorpusWriter.class
	jar cfm CorpusWriter.jar Manifest.CorpusWriter.txt mallet_helpers/CorpusWriter.class

clean:
	rm -rf lib
	rm mallet_helpers/CorpusWriter.class
