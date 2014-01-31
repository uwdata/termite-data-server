all: CorpusWriter.jar

mallet_helpers/CorpusWriter.class:
	javac -cp .:lib/mallet.jar:lib/mallet-deps.jar mallet_helpers/CorpusWriter.java

CorpusWriter.jar: mallet_helpers/CorpusWriter.class
	jar cfm CorpusWriter.jar Manifest.txt lib/* mallet_helpers/*.class

clean:
	rm CorpusWriter.jar
	rm mallet_helpers/*.class
