package mallet_helpers;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.lang.StringBuilder;
import java.util.ArrayList;

import gnu.trove.TIntArrayList;
import gnu.trove.TIntIntHashMap;
import cc.mallet.types.FeatureSequence;
import cc.mallet.types.Instance;
import cc.mallet.types.InstanceList;

public class CorpusWriter {
	public static String join(String[] tokens, String sep) {
		final StringBuilder sb = new StringBuilder();
		for (String token : tokens) {
			if (sb.length() > 0) {
				sb.append(sep);
			}
			sb.append(token);
		}
		return sb.toString();
	}
	public static void writeCorpusTokens(String inputFilename, String outputFilename) {
		System.err.println("Processing mallet corpus: [" + inputFilename + "] --> [" + outputFilename + "]");
		try {
			final File inputFile = new File(inputFilename);
			final InstanceList data = InstanceList.load(inputFile);
			final File outputFile = new File(outputFilename);
			final PrintStream writer = new PrintStream(outputFile);
			int count = 0;
			for (Instance instance : data) {
				if (count > 0 && count % 1000 == 0) {
					System.err.println("    processed " + count + " documents...");
				}
				final String docID = instance.getName().toString();
				final FeatureSequence features = (FeatureSequence) instance.getData();
				final String[] tokens = new String[features.getLength()];
				for (int i = 0; i < features.getLength(); i++) {
					tokens[i] = (String) features.getObjectAtPosition(i);
				}
				final String tokenStr = join(tokens, " ");
				writer.println(docID + "\t" + tokenStr);
				count++;
			}
			writer.close();
			System.err.println("    finished processing all " + count + " documents!");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	public static void main(String[] args) {
		if (args.length < 2) {
			System.err.println("Usage: java -jar [mallet-corpus] [output-corpus]");
			System.exit(-1);
		}
		final String inputFilename = args[0];
		final String outputFilename = args[1];
		writeCorpusTokens(inputFilename, outputFilename);
	}
}
