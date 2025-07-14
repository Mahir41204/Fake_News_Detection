import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from fever_evidence_corpus import FEVEREvidenceCorpus

# Advanced: Load FEVER evidence corpus
fever_corpus = FEVEREvidenceCorpus()
# Use all article chunks as the corpus
corpus = [v["content"] for v in fever_corpus.articles.values()]

embedder = SentenceTransformer("all-MiniLM-L6-v2")
corpus_embeddings = embedder.encode(corpus, convert_to_numpy=True)

# Create FAISS index
index = faiss.IndexFlatL2(corpus_embeddings.shape[1])
index.add(corpus_embeddings)

# 1. Load and prepare the LIAR dataset
# Download the train.tsv, test.tsv, valid.tsv from the LIAR dataset website
# and place them in a 'data' folder.
train_df = pd.read_csv(
    "data/train.tsv",
    sep="\t",
    header=None,
    names=[
        "id",
        "label",
        "statement",
        "subject",
        "speaker",
        "job_title",
        "state_info",
        "party_affiliation",
        "barely_true_counts",
        "false_counts",
        "half_true_counts",
        "mostly_true_counts",
        "pants_on_fire_counts",
        "context",
    ],
)
test_df = pd.read_csv(
    "data/test.tsv",
    sep="\t",
    header=None,
    names=[
        "id",
        "label",
        "statement",
        "subject",
        "speaker",
        "job_title",
        "state_info",
        "party_affiliation",
        "barely_true_counts",
        "false_counts",
        "half_true_counts",
        "mostly_true_counts",
        "pants_on_fire_counts",
        "context",
    ],
)


def simplify_label(label):
    if label in ["false", "pants-fire"]:
        return 0  # False
    elif label in ["barely-true", "half-true"]:
        return 1  # Half-True
    elif label in ["mostly-true", "true"]:
        return 2  # True
    return -1


train_df["label_id"] = train_df["label"].apply(simplify_label)
test_df["label_id"] = test_df["label"].apply(simplify_label)
train_df = train_df[train_df["label_id"] != -1]
test_df = test_df[test_df["label_id"] != -1]

train_dataset = Dataset.from_pandas(
    train_df[["statement", "label_id"]].rename(columns={"label_id": "labels"})
)
test_dataset = Dataset.from_pandas(
    test_df[["statement", "label_id"]].rename(columns={"label_id": "labels"})
)

# train_dataset = train_dataset.select(range(500))
# test_dataset = test_dataset.select(range(100))

model_name = "microsoft/deberta-v3-large"
# Use the slow tokenizer to avoid conversion errors
# (this fixes issues with tiktoken/SentencePiece on some platforms)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)


def retrieve_evidence(statement):
    embedding = embedder.encode([statement])[0]
    D, I = index.search(np.array([embedding]), k=1)
    return corpus[I[0][0]]


# Add retrieved evidence to the dataset
train_df["evidence"] = train_df["statement"].apply(retrieve_evidence)
test_df["evidence"] = test_df["statement"].apply(retrieve_evidence)

# New input: statement + evidence
train_df["input_text"] = train_df["statement"] + " [SEP] " + train_df["evidence"]
test_df["input_text"] = test_df["statement"] + " [SEP] " + test_df["evidence"]


def tokenize_function(examples):
    return tokenizer(examples["statement"], padding="max_length", truncation=True)


tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
tokenized_test_dataset = test_dataset.map(tokenize_function, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

training_args = TrainingArguments(
    output_dir="./results",
    # evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    push_to_hub=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_test_dataset,
)

trainer.train()

trainer.save_model("./my_misinformation_model")
tokenizer.save_pretrained("./my_misinformation_model")
print("Model fine-tuning complete and saved to './my_misinformation_model'")
