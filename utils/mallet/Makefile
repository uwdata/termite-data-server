all: CorpusWriter.jar

lib:
	mkdir lib
	
lib/mallet.jar: lib
	ln -s ../../../tools/mallet/dist/mallet.jar lib/mallet.jar

lib/mallet-deps.jar: lib
	ln -s ../../../tools/mallet/dist/mallet-deps.jar lib/mallet-deps.jar

mallet_helpers/CorpusWriter.class: lib/mallet.jar lib/mallet-deps.jar
	javac -cp .:lib/mallet.jar:lib/mallet-deps.jar mallet_helpers/CorpusWriter.java

CorpusWriter.jar: mallet_helpers/CorpusWriter.class
	jar cfm CorpusWriter.jar Manifest.txt lib/* mallet_helpers/*.class

clean:
	rm -rf lib
	rm mallet_helpers/CorpusWriter.class
