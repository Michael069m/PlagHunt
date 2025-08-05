import os
from sklearn.feature_extraction.text import TfidfVectorizer

def list_files(root):
    paths = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            relative_path = os.path.relpath(os.path.join(dirpath, f), root)
            paths.append(relative_path)
    return set(paths)

def compare_file_structure(path1, path2):
    files1 = list_files(path1)
    files2 = list_files(path2)

    overlap = files1.intersection(files2)
    overlap_ratio = len(overlap) / max(len(files1), 1)

    return overlap_ratio, overlap

def cosine_similarity_text(text1, text2):
    if not text1 or not text2:
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([text1, text2])
        similarity_matrix = (tfidf * tfidf.T)
        
        # Handle both sparse and dense matrices
        if hasattr(similarity_matrix, 'A'):
            similarity = similarity_matrix.A[0, 1]
        else:
            similarity = similarity_matrix[0, 1]
            
        return float(similarity)
    except Exception as e:
        print(f"Cosine similarity error: {e}")
        return 0.0
def compare_code_files(path1, path2):
    files1 = list_files(path1)
    files2 = list_files(path2)

    common_files = files1.intersection(files2)

    similarities = []
    for f in common_files:
        file1 = os.path.join(path1, f)
        file2 = os.path.join(path2, f)

        try:
            with open(file1, "r", encoding="utf-8") as f1:
                text1 = f1.read()
            with open(file2, "r", encoding="utf-8") as f2:
                text2 = f2.read()

            sim = cosine_similarity_text(text1, text2)
            similarities.append(sim)
        except:
            continue

    if similarities:
        avg_sim = sum(similarities) / len(similarities)
    else:
        avg_sim = 0.0

    return avg_sim
