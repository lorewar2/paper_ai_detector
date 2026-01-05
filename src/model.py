import torch
import torch.nn as nn
from torch.utils.data import Dataset
from transformers import BertModel

MAX_LEN = 512
STRIDE = 512
BATCH_SIZE = 16
EPOCHS = 3
LR = 1e-3
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class BertAIRegressor(nn.Module):
    def __init__(self, model_name="bert-base-uncased"):
        super().__init__()
        self.bert = BertModel.from_pretrained(model_name)

        # Freeze encoder
        for p in self.bert.parameters():
            p.requires_grad = False

        hidden = self.bert.config.hidden_size

        self.regressor = nn.Sequential(
            nn.Linear(hidden, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 1)
        )

    def mean_pooling(self, hidden_states, attention_mask):
        mask = attention_mask.unsqueeze(-1).float()
        summed = torch.sum(hidden_states * mask, dim=1)
        counts = torch.clamp(mask.sum(dim=1), min=1e-9)
        return summed / counts

    def forward(self, input_ids, attention_mask):
        with torch.no_grad():
            outputs = self.bert(
                input_ids=input_ids,
                attention_mask=attention_mask
            )

        pooled = self.mean_pooling(
            outputs.last_hidden_state,
            attention_mask
        )

        score = self.regressor(pooled)
        score = torch.sigmoid(score) * 100
        return score.squeeze(-1)

def chunk_text(text, tokenizer, max_len=MAX_LEN, stride=STRIDE):
    tokens = tokenizer(
        text,
        add_special_tokens=False,
        return_attention_mask=False
    )["input_ids"]

    chunks = []
    for i in range(0, len(tokens), stride):
        chunk_tokens = tokens[i:i + max_len]

        encoded = tokenizer.prepare_for_model(
            chunk_tokens,
            max_length=max_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

        chunks.append({
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0)
        })

    return chunks

class ChunkedDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.samples = []

        for text, label in zip(texts, labels):
            chunks = chunk_text(text, tokenizer)
            for chunk in chunks:
                self.samples.append({
                    "input_ids": chunk["input_ids"],
                    "attention_mask": chunk["attention_mask"],
                    "label": torch.tensor(label, dtype=torch.float)
                })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]

def train(model, dataloader):
    model.train()
    model.to(DEVICE)

    optimizer = torch.optim.AdamW(
        model.regressor.parameters(),
        lr=LR
    )
    loss_fn = nn.MSELoss()

    for epoch in range(EPOCHS):
        total_loss = 0.0

        for batch in dataloader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["label"].to(DEVICE)

            preds = model(input_ids, attention_mask)
            loss = loss_fn(preds, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss / len(dataloader):.4f}")


def score_long_document(text, model, tokenizer):
    model.eval()
    chunks = chunk_text(text, tokenizer)
    scores = []

    with torch.no_grad():
        for chunk in chunks:
            input_ids = chunk["input_ids"].unsqueeze(0).to(DEVICE)
            attention_mask = chunk["attention_mask"].unsqueeze(0).to(DEVICE)
            score = model(input_ids, attention_mask)
            scores.append(score.item())

    return max(scores)

