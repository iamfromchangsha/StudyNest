import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def smart_sentence_split(text):
    """
    智能分句，避免在数字序号（如 7.3.1）或小数中切分。
    规则：按 。！？； 分割，但要求这些标点后面不紧跟数字（避免分割小数点/序号），
    且标点后是空格或汉字开头（更符合中文习惯）。
    """
    # 使用零宽断言：句号、感叹号、问号、分号后跟空白或汉字，且前面不是数字（避免分割小数点）
    # 但简单地判断后面不跟数字即可避免分割序号，但像“你好。你好”仍可分割。
    # 这里采用：标点后是空白或中文字符，且标点前不是数字（如果是数字，可能为序号或小数）
    # 更简单的做法：直接按标点分割，但排除数字序号中的点，我们通过后续过滤处理。
    # 这里使用一个常用模式：分割符为 [。！？；] 后面跟着空白或汉字开头，但为了兼容，直接按这些标点分割，然后合并过短的片段。
    sentences = re.split(r'[。！？；]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def is_garbage_line(line):
    """
    判断一行（或句子）是否主要由乱码/特殊符号组成
    规则：如果非中文字符、非英文字母、非数字的字符占比超过 50%，则认为是乱码行。
    """
    if not line:
        return True
    total_chars = len(line)
    # 统计中文字符、英文字母、数字
    valid_chars = len(re.findall(r'[\u4e00-\u9fff]|[a-zA-Z0-9]', line))
    if total_chars == 0:
        return True
    return (total_chars - valid_chars) / total_chars > 0.5

def preprocess_text_robust(text):
    """
    改进的预处理：分句 + 清洗乱码句 + 过滤过短句
    """
    # 先进行简单分句
    raw_sentences = smart_sentence_split(text)
    
    # 进一步按换行符分割（PPT文本可能含有换行）
    expanded = []
    for s in raw_sentences:
        # 如果句子内包含换行，再按换行细分
        parts = s.split('\n')
        for p in parts:
            p = p.strip()
            if p:
                expanded.append(p)
    
    # 过滤乱码句和过短句（少于5个字符）
    cleaned = []
    for sent in expanded:
        if len(sent) < 5:
            continue
        if is_garbage_line(sent):
            continue
        cleaned.append(sent)
    
    return cleaned

def extractive_summarize_tfidf_robust(text: str, num_sentences: int) -> str:
    """
    使用 TF-IDF 进行抽取式摘要（增强版，对公式符号更鲁棒）
    """
    sentences = preprocess_text_robust(text)

    if len(sentences) <= num_sentences:
        print("警告：请求的句子数大于等于总句子数，返回原文。")
        return text

    # 自定义 token_pattern：只匹配中文字符和英文单词（至少两个字母的英文单词）
    # 注意：对于中文，默认是按字符切分（因为中文无空格），这通常足够。
    # 但为了更好，我们可以使用 jieba 分词，这里为了简单，保留字符级。
    # 设置 token_pattern 忽略纯数字和符号，只保留中文字符和字母组合。
    # 由于 TfidfVectorizer 的 token_pattern 是针对整个 token 的，我们可以用 regex 来定义 token：
    # 匹配连续的字母或中文字符（但中文是单个字符，会被视为多个 token）。
    # 这样数字和符号就不会被纳入特征。
    vectorizer = TfidfVectorizer(
        token_pattern=r'(?u)[\u4e00-\u9fff]+|[a-zA-Z]{2,}',  # 中文字符（每个字符单独成token）或至少两个字母的英文单词
        lowercase=True,
        max_df=0.8,       # 忽略在过多文档中出现的词（可选）
        min_df=1,         # 忽略出现次数过少的词
    )
    # 注意：token_pattern 是用于从每个句子中提取 token 的，这里我们让每个中文字符作为一个 token，英文单词作为 token。
    # 这会导致特征维度较高，但能有效过滤符号。

    tfidf_matrix = vectorizer.fit_transform(sentences)

    # 计算文档平均向量（所有句子向量的平均）
    doc_avg = np.mean(tfidf_matrix.toarray(), axis=0)

    # 计算每个句子与文档平均向量的余弦相似度
    sentence_scores = []
    for i in range(len(sentences)):
        vec = tfidf_matrix[i].toarray()[0]
        # 防止零向量（如果句子全由停用词或符号组成，过滤后可能为零）
        norm_vec = np.linalg.norm(vec)
        norm_doc = np.linalg.norm(doc_avg)
        if norm_vec == 0 or norm_doc == 0:
            score = 0.0
        else:
            score = np.dot(vec, doc_avg) / (norm_vec * norm_doc)
        sentence_scores.append((score, i))

    # 按分数降序，取前 num_sentences 个句子索引
    ranked = sorted(sentence_scores, key=lambda x: x[0], reverse=True)
    top_indices = sorted([idx for _, idx in ranked[:num_sentences]])

    # 按原序拼接摘要（添加句号，如果原句末尾没有标点）
    summary = ""
    for idx in top_indices:
        sent = sentences[idx]
        if sent[-1] not in "。！？；":
            sent += "。"
        summary += sent

    return summary

# ========== 新增的高级封装函数 ==========
def summarize(text, ratio=0.4):
    """
    自动对文本进行抽取式摘要，返回压缩后的文字。

    Args:
        text: 输入的长文本。
        ratio: 压缩比例，目标句子数 = max(1, int(原句数 * ratio))，默认0.4。

    Returns:
        摘要文本。
    """
    # 先获取清洗后的句子数，计算目标句子数
    sentences = preprocess_text_robust(text)
    num_sentences = max(1, int(len(sentences) * ratio))
    # 调用底层摘要函数
    return extractive_summarize_tfidf_robust(text, num_sentences)

# --- 示例使用 ---
if __name__ == "__main__":
    # 请将您的长文本赋值给这个变量
    with open(r"D:\GitHub\xiaoya_2\download\6857762219124377374\第12章 预应力混凝土结构的概念及其材料.txt", "r", encoding="utf-8") as f:
        long_material = f.read()


    # 使用高级函数进行摘要（默认压缩到原句数的40%）
    compressed = summarize(long_material)

    print("--- 压缩前 ---")
    print(f"原文字数: {len(long_material)}")
    print(f"原句数: {len(preprocess_text_robust(long_material))}")
    print("\n--- 压缩后 ---")
    print(f"摘要字数: {len(compressed)}")
    print(f"摘要句数: {len(preprocess_text_robust(compressed))}")
    print(compressed)