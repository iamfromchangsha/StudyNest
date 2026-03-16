import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def preprocess_text(text):
    """简单的文本预处理"""
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 按句号、问号、感叹号分割句子
    sentences = re.split(r'[。！？\n]', text)
    # 过滤掉空字符串或非常短的句子
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    return sentences

def extractive_summarize_tfidf(text: str, num_sentences: int) -> str:
    """
    使用 TF-IDF 和余弦相似度进行抽取式摘要。

    Args:
        text: 输入的长文本。
        num_sentences: 希望提取的句子数量。

    Returns:
        摘要文本。
    """
    sentences = preprocess_text(text)

    if len(sentences) <= num_sentences:
        print("警告：请求的句子数大于等于总句子数，返回原文。")
        return text

    # 1. 计算 TF-IDF 矩阵
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)

    # 2. 计算每个句子与整个文档的平均相似度（作为其重要性评分）
    doc_averages = np.mean(tfidf_matrix.toarray(), axis=0)
    sentence_scores = []
    
    for i in range(len(sentences)):
        sentence_vec = tfidf_matrix[i].toarray()[0]
        score = np.dot(sentence_vec, doc_averages) / (np.linalg.norm(sentence_vec) * np.linalg.norm(doc_averages) + 1e-8)
        sentence_scores.append((score, i))

    # 3. 排序并选取 top-N 句子
    ranked_sentences = sorted(sentence_scores, key=lambda x: x[0], reverse=True)
    top_sentence_indices = sorted([i for _, i in ranked_sentences[:num_sentences]]) # 保持原始顺序
    
    # 4. 组合摘要
    summary = "".join([sentences[i] + "。" for i in top_sentence_indices])
    return summary

def summarize(text: str, compression_ratio: float = 0.4) -> str:
    """
    自动对文本进行抽取式摘要，返回压缩后的文字。

    Args:
        text: 输入的长文本。
        compression_ratio: 压缩比例，目标句子数 = 原句数 * compression_ratio，默认0.4。

    Returns:
        摘要文本。
    """
    sentences = preprocess_text(text)
    # 至少保留1个句子
    num_sentences = max(1, int(len(sentences) * compression_ratio))
    return extractive_summarize_tfidf(text, num_sentences)

# --- 示例使用 ---
if __name__ == "__main__":
    # 请将您的长文本赋值给这个变量
    long_material = """
    这里放入您的长文本内容。例如：
    人工智能（Artificial Intelligence，简称AI）是一门研究、开发用于模拟和扩展人类智能的理论、方法、技术及应用系统的科学。
    自20世纪50年代诞生以来，人工智能经历了多次兴衰，如今已成为科技领域的热点。
    机器学习是人工智能的一个重要分支，它通过算法让计算机从数据中学习规律，从而做出预测或决策。
    深度学习则是机器学习的一个子集，利用多层神经网络自动提取特征，在图像识别、语音识别等领域取得了巨大成功。
    自然语言处理（NLP）也是人工智能的重要方向，它让计算机能够理解、解释和生成人类语言，例如机器翻译、聊天机器人等。
    随着算力的提升和大数据的积累，人工智能正在深刻改变各行各业，如医疗、金融、交通、教育等。
    """

    # 调用自动摘要函数（默认压缩到原句数的40%）
    compressed_material = summarize(long_material)

    print("--- 压缩前 ---")
    print(f"原文字数: {len(long_material)}")
    print(f"原句数: {len(preprocess_text(long_material))}")
    print("\n--- 压缩后 ---")
    print(f"摘要字数: {len(compressed_material)}")
    print(f"摘要句数: {len(preprocess_text(compressed_material))}")
    print(compressed_material)