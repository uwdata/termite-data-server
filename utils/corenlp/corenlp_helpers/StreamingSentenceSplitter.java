package corenlp_helpers;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.List;
import java.util.Properties;

import edu.stanford.nlp.ling.CoreAnnotations.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.util.CoreMap;

public class StreamingSentenceSplitter {
	public static void process() {
		System.err.println("Preparing the Stanford CoreNLP pipeline...");
		final Properties props = new Properties();
		props.put("annotators", "tokenize, ssplit");
		final StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

		System.err.println("Processing corpus...");
		try {
			final InputStreamReader reader = new InputStreamReader(System.in, "UTF-8");
			final OutputStreamWriter writer = new OutputStreamWriter(System.out, "UTF-8");
			final BufferedReader in = new BufferedReader(reader);
			final BufferedWriter out = new BufferedWriter(writer);
			while (true) {
				final String line = in.readLine();
				if ((line == null) || (line.length() == 0)) {
					break;
				}
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
					out.write(docID+"\t"+sentenceIndex+"\t"+text);
					out.newLine();
					out.flush();
				}
			}
			in.close();
			out.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	public static void main(String[] args) {
		process();
	}
}
