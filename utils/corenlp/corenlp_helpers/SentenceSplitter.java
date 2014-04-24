package corenlp_helpers;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.File;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.List;
import java.util.Properties;

import edu.stanford.nlp.ling.CoreAnnotations.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.util.CoreMap;

public class SentenceSplitter {
	public static void process(String inputFilename, String outputFilename) {
		System.err.println("Preparing the Stanford CoreNLP pipeline...");
		final Properties props = new Properties();
		props.put("annotators", "tokenize, ssplit");
		final StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

		System.err.println("Processing corpus: [" +inputFilename+ "] -> [" +outputFilename+ "]");
		try {
			final File inputFile = new File(inputFilename);
			final FileInputStream inputStream = new FileInputStream(inputFile);
			final InputStreamReader reader = new InputStreamReader(inputStream, "UTF-8");
			final BufferedReader in = new BufferedReader(reader);
			
			final File outputFile = new File(outputFilename);
			final FileOutputStream outputStream = new FileOutputStream(outputFile);
			final OutputStreamWriter writer = new OutputStreamWriter(outputStream, "UTF-8");
			final BufferedWriter out = new BufferedWriter(writer);
			
			String line;
			while ((line = in.readLine()) != null) {
				final String[] fields = line.split("\\t");
				final String docID = fields[0];
				final String docContent = fields[1];
				final Annotation document = new Annotation(docContent);
				pipeline.annotate(document);
				final List<CoreMap> sentences = document.get(SentencesAnnotation.class);
				int sentenceIndex = 0;
				for (CoreMap sentence : sentences) {
					final String text = sentence.get(TextAnnotation.class);
					sentenceIndex++;
					out.write(docID+"::"+sentenceIndex+"\t"+text);
					out.newLine();
				}
			}
			
			in.close();
			reader.close();
			out.close();
			writer.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	public static void main(String[] args) {
		if (args.length < 2) {
			System.err.println("Usage: java -jar [input-file] [output-file]");
			System.exit(-1);
		}
		final String inputFilename = args[0];
		final String outputFilename = args[1];
		process(inputFilename, outputFilename);
	}
}
