all: SentenceSplitter.jar

lib:
	mkdir lib
	ln -s ../../../tools/corenlp-3.3.1/stanford-corenlp-3.3.1.jar lib/stanford-corenlp-3.3.1.jar
	ln -s ../../../tools/corenlp-3.3.1/stanford-corenlp-3.3.1-models.jar lib/stanford-corenlp-3.3.1-models.jar

corenlp_helpers/SentenceSplitter.class: lib corenlp_helpers/SentenceSplitter.java
	javac -cp .:lib/stanford-corenlp-3.3.1.jar:lib/stanford-corenlp-3.3.1-models.jar corenlp_helpers/SentenceSplitter.java

SentenceSplitter.jar: corenlp_helpers/SentenceSplitter.class
	jar cfm SentenceSplitter.jar Manifest.SentenceSplitter.txt corenlp_helpers/SentenceSplitter.class

clean:
	rm -rf lib
	rm corenlp_helpers/SentenceSplitter.class
