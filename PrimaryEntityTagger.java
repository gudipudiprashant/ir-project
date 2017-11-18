import java.io.*;
import java.util.*;
import org.apache.commons.lang3.tuple.Pair;

import edu.stanford.nlp.coref.CorefCoreAnnotations;

import edu.stanford.nlp.coref.data.CorefChain;
import edu.stanford.nlp.io.*;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations;
import edu.stanford.nlp.sentiment.SentimentCoreAnnotations;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.util.*;


public class PrimaryEntityTagger {
	private final static String NNP = "NNP";
	private final static String NN = "NN";
	private final static String NNS = "NNS";
	private final static String OF = "OF";

	private static enum NamedEntityType {
		NONE("O"),
		ORG("ORGANIZATION"),
		PERSON("PERSON"),
		LOCATION("LOCATION"),
		DATE("DATE"),
		NUMBER("NUMBER");

		public final String nlpString;

		NamedEntityType(final String s) {
			nlpString = s;
		}
	};

	private Annotation annotation;
	private String inputFile;

	private static final Map<String, Boolean> primaryKeywordMap = new HashMap<>();
	private Map<String, List<Pair<String, Integer>>> primaryEntities = new HashMap<>();
	static {
		List<String> wordList = Arrays.asList(
			"killed",
			"shot", "shooting",
			"bombed",	
			"died", "dead", 
			"attacked",
			"injured",
			"gunned",
			"attacked",
			"terrorist", "terrorism"
		);

		for (String word: wordList) {
			primaryKeywordMap.put(word, true);
		}
	}

	private Map<CoreMap, Boolean> primSentMap = new HashMap<>();
	private Map<CoreMap, Boolean> secSentMap = new HashMap<>();


	public PrimaryEntityTagger(Annotation annotation, final String fileName) {
		this.annotation = annotation;
		this.inputFile = fileName;

		for (NamedEntityType net: NamedEntityType.values()) {
			if (net == NamedEntityType.NONE)
				continue;

			primaryEntities.put(net.nlpString, new ArrayList<Pair<String, Integer>>());
		}
	}

	private boolean isNoun(final String s) {
		return (s.equalsIgnoreCase(NN)) || (s.equalsIgnoreCase(NNP))
				|| s.equalsIgnoreCase(NNS) || s.equalsIgnoreCase(OF);
	}


	public boolean parseSentence(final CoreMap sentence, Map<String, List<Pair<String, Integer>>> entities) {
		List<CoreLabel> tokens = sentence.get(CoreAnnotations.TokensAnnotation.class);
		for (int i = 0; i < tokens.size();) {
			CoreLabel token = tokens.get(i); String posString = token.get(CoreAnnotations.PartOfSpeechAnnotation.class);
			String entityType = token.ner();
			if (!entityType.equals(NamedEntityType.NONE.nlpString)
					&& entities.containsKey(entityType)) {
				String fullToken = "";
				if (entityType.equals(NamedEntityType.NUMBER.nlpString)) {
					while (i < tokens.size() && tokens.get(i)
							.ner().equalsIgnoreCase(NamedEntityType.NUMBER.nlpString)) {
						fullToken += tokens.get(i).originalText() + " ";
						i++;
					}
					if (i < tokens.size()) {
						fullToken += tokens.get(i++).originalText() + " ";
					}
				}
				else {
					while (i < tokens.size() && tokens.get(i)
								.get(CoreAnnotations.PartOfSpeechAnnotation.class).equalsIgnoreCase(posString)) {
						fullToken += tokens.get(i).originalText() + " ";
						i++;
					}
				}
				
				entities.get(entityType).add(Pair.of(fullToken, token.beginPosition()));
			}
			else {
				i++;
			}
		}
		return true;
	}

	// What exceptions do we throw here?
	public boolean tagPrimary() {
		// An Annotation is a Map with Class keys for the linguistic analysis types.
		// You can get and use the various analyses individually.
		// For instance, this gets the parse tree of the first sentence in the text.
		List<CoreMap> sentences = annotation.get(CoreAnnotations.SentencesAnnotation.class);
		
		if (sentences == null || sentences.isEmpty()) {
			return false;
		}

		int sentenceIdx = 0;
		for (CoreMap sentence: sentences) {
			boolean isImportant = false;
			for (CoreLabel token: sentence.get(CoreAnnotations.TokensAnnotation.class)) {
				String tokenText = token.originalText();
				if (primaryKeywordMap.containsKey(tokenText)) {
					isImportant = true; break;
				}
			}

			if (isImportant) {
				primSentMap.put(sentence, true);
				parseSentence(sentence, primaryEntities);
			}

			sentenceIdx++;
		}	

		return true;
	}

	public void dumpNerInfo(PrintWriter out) {
		List<CoreMap> sentences = annotation.get(CoreAnnotations.SentencesAnnotation.class);
		if (sentences == null || sentences.isEmpty()) {
			return;
		}
		int sentenceIdx = 0;
		out.println("[");
		for (CoreMap sentence: sentences) {
			out.println("[");
			for (CoreLabel token: sentence.get(CoreAnnotations.TokensAnnotation.class)) {
				out.println("{");
				String tokenText = token.originalText();
				out.println("\"tokentext\": \"" + tokenText + "\",");
				String entityType = token.ner();
				if (!entityType.equals(NamedEntityType.NONE.nlpString)) {
					out.println("\"netype\": \"" + entityType + "\"");
				}
				out.println("},");
			}
			out.println("],");
			sentenceIdx++;
		}
		out.println("]");
	}

    public void dumpCorefInfo(PrintWriter out) {
//        System.out.println("Coreference information");
        Map<Integer, CorefChain> corefChains =
            annotation.get(CorefCoreAnnotations.CorefChainAnnotation.class);
		out.println("[");
        if (corefChains == null) { return; }
        for (Map.Entry<Integer,CorefChain> entry: corefChains.entrySet()) {
			out.println("[");
            for (CorefChain.CorefMention m : entry.getValue().getMentionsInTextualOrder()) {
				out.println("{");
				// We need to subtract one since the indices count from 1 but the Lists start from 0
				// List<CoreLabel> tokens = sentences.get(m.sentNum - 1).gedet(CoreAnnotations.TokensAnnotation.class);
				out.println("\"sentnum\":" + (m.sentNum - 1) + ",\n"
							+ "\"startindex\":" + (m.startIndex - 1) + ",\n"
							+ "\"endindex\":" + (m.endIndex - 2));
				out.println("},");
			}
			out.println("],");
        }
		out.println("]");
    }

	public Map<String, List<Pair<String, Integer>>> tagCoref() {
		Map<Integer, CorefChain> corefChains =
		    annotation.get(CorefCoreAnnotations.CorefChainAnnotation.class);
		List<CoreMap> sentences = annotation.get(CoreAnnotations.SentencesAnnotation.class);
		if (corefChains == null || sentences == null) { 
			return null; 
		}

		Map<String, List<Pair<String, Integer>>> secEntities = new HashMap<>();
		for (NamedEntityType net: NamedEntityType.values()) {
			if (net == NamedEntityType.NONE)
				continue;

			secEntities.put(net.nlpString, new ArrayList<Pair<String, Integer>>());
		}

		for (Map.Entry<Integer,CorefChain> entry: corefChains.entrySet()) {
		  // For each chain, itearte through the mentions
		  for (CorefChain.CorefMention m : entry.getValue().getMentionsInTextualOrder()) {
		  	if (primSentMap.containsKey(sentences.get(m.sentNum - 1))
		  			|| secSentMap.containsKey(sentences.get(m.sentNum - 1))) {
		  		continue;
		  	}
		    List<CoreLabel> tokens = sentences.get(m.sentNum - 1).get(CoreAnnotations.TokensAnnotation.class);
		    if (parseSentence(sentences.get(m.sentNum - 1), secEntities))
		    	secSentMap.put(sentences.get(m.sentNum - 1), true);

		    // We subtract two for end: one for 0-based indexing, and one because we want last token of mention not one following.
		    // out.println("  " + m + ", i.e., 0-based character offsets [" + tokens.get(m.startIndex - 1).beginPosition() +
		    //         ", " + tokens.get(m.endIndex - 2).endPosition() + ")");
		  }
		}

		return secEntities;
	}


	public Map<String, List<Pair<String, Integer>>> getPrimaryEntities() {
		return primaryEntities;
	}

    public static void main(String[] args) throws IOException {
		BufferedReader bufferedReader = null;
		if (args.length < 1) {
			System.out.println("Error: missing input file");
			System.exit(1);
		}
		try {
			File file = new File(args[0]);
			bufferedReader = new BufferedReader(new FileReader(file));

		} catch (IOException e) {
			e.printStackTrace();
			System.exit(1);
		}

		// Add in sentiment
		Properties props = new Properties();
		props.setProperty("annotators", "tokenize, ssplit, pos, lemma, ner, parse, dcoref");
		StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
		String filename;
		while ((filename = bufferedReader.readLine()) != null) {
			// Initialize an Annotation with some text to be annotated. The text is the argument to the constructor.
			Annotation annotation;
			annotation = new Annotation(IOUtils.slurpFileNoExceptions(filename));
			// run all the selected Annotators on this text
			pipeline.annotate(annotation);
			// So far we have annotated the pipeline and now we call the PrimaryENtityTagger
			PrimaryEntityTagger pet = new PrimaryEntityTagger(annotation, filename);
//			System.out.println("================== Tagged and annotated, ready to show primary");
			PrintWriter out = new PrintWriter(filename + ".ner");
			out.println("{");
			out.println("\"ner\": ");
			pet.dumpNerInfo(out);
			out.println(",");
			out.println("\"coref\": ");
			pet.dumpCorefInfo(out);
			out.println("}");
			out.flush(); out.close();
			System.out.println("Done with: " + filename + ".ner");
		}
    }
}