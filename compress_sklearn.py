import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'[。！？\n]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    return sentences

def extractive_summarize_tfidf(text: str, num_sentences: int) -> str:

    sentences = preprocess_text(text)

    if len(sentences) <= num_sentences:
        print("警告：请求的句子数大于等于总句子数，返回原文。")
        return text

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)

    doc_averages = np.mean(tfidf_matrix.toarray(), axis=0)
    sentence_scores = []
    
    for i in range(len(sentences)):
        sentence_vec = tfidf_matrix[i].toarray()[0]
        score = np.dot(sentence_vec, doc_averages) / (np.linalg.norm(sentence_vec) * np.linalg.norm(doc_averages) + 1e-8)
        sentence_scores.append((score, i))

    ranked_sentences = sorted(sentence_scores, key=lambda x: x[0], reverse=True)
    top_sentence_indices = sorted([i for _, i in ranked_sentences[:num_sentences]]) # 保持原始顺序
    
    summary = "".join([sentences[i] + "。" for i in top_sentence_indices])
    return summary

def summarize(text: str, compression_ratio: float = 0.4) -> str:

    sentences = preprocess_text(text)
    num_sentences = max(1, int(len(sentences) * compression_ratio))
    return extractive_summarize_tfidf(text, num_sentences)
