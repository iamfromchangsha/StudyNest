import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def smart_sentence_split(text):

    sentences = re.split(r'[。！？；]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def is_garbage_line(line):

    if not line:
        return True
    total_chars = len(line)
    valid_chars = len(re.findall(r'[\u4e00-\u9fff]|[a-zA-Z0-9]', line))
    if total_chars == 0:
        return True
    return (total_chars - valid_chars) / total_chars > 0.5

def preprocess_text_robust(text):

    raw_sentences = smart_sentence_split(text)
    
    expanded = []
    for s in raw_sentences:
        parts = s.split('\n')
        for p in parts:
            p = p.strip()
            if p:
                expanded.append(p)
    
    cleaned = []
    for sent in expanded:
        if len(sent) < 5:
            continue
        if is_garbage_line(sent):
            continue
        cleaned.append(sent)
    
    return cleaned

def extractive_summarize_tfidf_robust(text: str, num_sentences: int) -> str:

    sentences = preprocess_text_robust(text)

    if len(sentences) <= num_sentences:
        print("警告：请求的句子数大于等于总句子数，返回原文。")
        return text

    
    vectorizer = TfidfVectorizer(
        token_pattern=r'(?u)[\u4e00-\u9fff]+|[a-zA-Z]{2,}',  
        lowercase=True,
        max_df=0.8,       
        min_df=1,         
    )


    tfidf_matrix = vectorizer.fit_transform(sentences)

    doc_avg = np.mean(tfidf_matrix.toarray(), axis=0)

    sentence_scores = []
    for i in range(len(sentences)):
        vec = tfidf_matrix[i].toarray()[0]
        norm_vec = np.linalg.norm(vec)
        norm_doc = np.linalg.norm(doc_avg)
        if norm_vec == 0 or norm_doc == 0:
            score = 0.0
        else:
            score = np.dot(vec, doc_avg) / (norm_vec * norm_doc)
        sentence_scores.append((score, i))

    ranked = sorted(sentence_scores, key=lambda x: x[0], reverse=True)
    top_indices = sorted([idx for _, idx in ranked[:num_sentences]])

    summary = ""
    for idx in top_indices:
        sent = sentences[idx]
        if sent[-1] not in "。！？；":
            sent += "。"
        summary += sent

    return summary

def summarize(text, ratio=0.4):

    sentences = preprocess_text_robust(text)
    num_sentences = max(1, int(len(sentences) * ratio))
    return extractive_summarize_tfidf_robust(text, num_sentences)

