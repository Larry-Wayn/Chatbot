import os
import json
import hashlib
import logging
import chardet
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


class Config:
    JSON_PATH = "resource/database/NeZha.json"
    SAVE_PATH = "resource/database"
    LOG_PATH = "logs"
    MODEL_NAME = "text2vec-large-chinese"

    # 检索参数
    min_similarity = 0.8   # 相似度阈值
    default_k = 5          # 默认返回结果数
    search_multiplier = 5  # 搜索扩展倍数

    # 对话参数
    max_history = 20       # 保留的历史消息数
    max_context_len = 1000 # 上下文最大长度（字符）


def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)

        if result["confidence"] < 0.85:
            return _try_common_encodings(raw_data)

        encoding = result["encoding"].lower()
        encoding_map = {
            "gb2312": "gb18030",
            "ascii": "utf-8",
            "windows-1252": "utf-8",
        }
        return encoding_map.get(encoding, encoding)


def _try_common_encodings(data):
    for encoding in ["utf-8-sig", "gb18030", "utf-16", "big5"]:
        try:
            data.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return "utf-8"


def process_value(value):
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            processed_v = process_value(v)
            parts.append(f"{k}：{processed_v}")
        return "；".join(parts)
    elif isinstance(value, list):
        return "、".join(map(str, value))
    else:
        return str(value)


def extract_text(data):
    result = []
    data = data.get("数据库")
    for top_key in data:
        top_data = data[top_key]
        if not isinstance(top_data, dict):
            continue
        for role_name in top_data:
            role_data = top_data[role_name]
            if not isinstance(role_data, dict):
                continue
            for third_key in role_data:
                third_value = role_data[third_key]
                content = process_value(third_value)
                entry = f"{top_key}-{role_name}-{third_key}：{content}"
                result.append(entry)
    return result


class TextEmbedding:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(model_name=Config.MODEL_NAME)
        self.db = self._load_or_create_embeddings()

    def _calculate_hash(self, file_path):
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def _load_or_create_embeddings(self):
        hash_file = f"{Config.SAVE_PATH}/db_hash.txt"
        current_hash = self._calculate_hash(Config.JSON_PATH)

        if os.path.exists(Config.SAVE_PATH) and os.path.exists(hash_file):
            with open(hash_file, "r") as f:
                saved_hash = f.read().strip()
            if saved_hash == current_hash:
                logging.info("知识库已存在且未改变，直接加载...")
                return FAISS.load_local(
                    Config.SAVE_PATH,
                    self.model,
                    allow_dangerous_deserialization=True,
                )
            else:
                logging.warning("知识库已改变，重新初始化...")

        logging.info("初始化知识库...")
        encoding = detect_encoding(Config.JSON_PATH)
        try:
            with open(Config.JSON_PATH, "r", encoding=encoding) as f:
                data = json.load(f)
        except UnicodeDecodeError:
            logging.error(f"编码检测失败 ({encoding})，尝试强制解码")
            with open(Config.JSON_PATH, "r", encoding=encoding, errors="replace") as f:
                data = json.load(f)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        documents = []
        for text in extract_text(data):
            documents.extend(text_splitter.create_documents([text]))

        db = FAISS.from_documents(documents, self.model)
        db.save_local(Config.SAVE_PATH)
        with open(hash_file, "w") as f:
            f.write(current_hash)
        logging.info("知识库初始化完成并已保存。")
        return db

    def _retrieve_context(self, query):
        logging.info(f"Query: {query}")
        results = self.db.similarity_search(query, Config.default_k)
        for i, result in enumerate(results):
            logging.info(f"结果 {i + 1}: {result.page_content}")
        return results