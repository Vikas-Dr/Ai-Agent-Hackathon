"""
Quick-Start Code Sandbox Generator for DevPulse.
Auto-generates 10-line starter code templates for DevRel recommendations.
"""

from typing import Optional


SANDBOX_TEMPLATES = {
    "API Design": {
        "python": '''from fastapi import FastAPI
app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """Get item by ID"""
    return {"item_id": item_id, "name": "Example"}

# Run: uvicorn main:app --reload
# Docs: http://localhost:8000/docs''',
        "javascript": '''import express from 'express';
const app = express();

app.get('/items/:id', (req, res) => {
  res.json({ item_id: req.params.id, name: 'Example' });
});

app.listen(3000);
console.log('Server running on port 3000');
// Docs: http://localhost:3000/items/1'''
    },
    
    "Authentication": {
        "python": '''from fastapi import FastAPI, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

app = FastAPI()
security = HTTPBearer()

@app.post("/login")
async def login(username: str, password: str):
    token = jwt.encode({"sub": username}, "secret")
    return {"access_token": token}

# Protect endpoints with @app.get(..., dependencies=[Depends(security)])''',
        "javascript": '''import jwt from 'jsonwebtoken';

const login = (username, password) => {
  const token = jwt.sign({ sub: username }, 'secret');
  return { access_token: token };
};

const verify = (token) => {
  try { return jwt.verify(token, 'secret'); }
  catch (e) { return null; }
};'''
    },
    
    "WebAssembly": {
        "rust": '''#[wasm_bindgen]
pub fn add(a: u32, b: u32) -> u32 {
    a + b
}

#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

// Build: wasm-pack build --release
// Use in JS: import { add, greet }''',
        "javascript": '''const wasmModule = await WebAssembly.instantiateStreaming(
  fetch('module.wasm')
);
const { add, greet } = wasmModule.instance.exports;

console.log(add(5, 3));      // 8
console.log(greet("World")); // Hello, World!'''
    },
    
    "Cloud Infrastructure": {
        "python": '''from google.cloud import storage
import os

bucket_name = "my-bucket"
client = storage.Client()
bucket = client.bucket(bucket_name)

blob = bucket.blob("file.txt")
blob.upload_from_string("Hello Cloud!")

# List files
for blob in bucket.list_blobs(): print(blob.name)''',
        "terraform": '''resource "aws_s3_bucket" "example" {
  bucket = "my-unique-bucket"
}

resource "aws_s3_object" "file" {
  bucket = aws_s3_bucket.example.id
  key    = "hello.txt"
  source = "hello.txt"
}'''
    },
    
    "DevOps & CI/CD": {
        "yaml": '''name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install pytest
      - run: pytest tests/
      - run: python -m flake8 src/''',
        "python": '''import subprocess
import sys

def run_tests():
    result = subprocess.run([sys.executable, '-m', 'pytest'], cwd='tests/')
    return result.returncode == 0

if __name__ == '__main__': run_tests()'''
    },
    
    "Database & Data": {
        "python": '''from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()
engine = create_engine("sqlite:///db.sqlite")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)

Base.metadata.create_all(engine)''',
        "sql": '''CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE
);

INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
SELECT * FROM users WHERE id = 1;'''
    },
    
    "Python & Data Science": {
        "python": '''import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

df = pd.read_csv('data.csv')
X = df[['feature1', 'feature2']]
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
print(f"Training set: {X_train.shape}")'''
    },
    
    "Web Security": {
        "python": '''from cryptography.fernet import Fernet
import hashlib

# Generate key
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
message = b"Secret data"
encrypted = cipher.encrypt(message)

# Decrypt
decrypted = cipher.decrypt(encrypted)
print(decrypted)''',
        "javascript": '''// Hash password (use bcrypt in production)
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash('password123', 10);
const isValid = await bcrypt.compare('password123', hash);

// Sanitize HTML
const DOMPurify = require('isomorphic-dompurify');
const clean = DOMPurify.sanitize(userInput);'''
    },
    
    "Frontend Frameworks": {
        "javascript": '''import React, { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}''',
        "typescript": '''interface User {
  id: number;
  name: string;
  email: string;
}

const fetchUser = async (id: number): Promise<User> => {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
};'''
    },
    
    "Mobile Development": {
        "swift": '''import SwiftUI

struct ContentView: View {
    @State var count = 0
    var body: some View {
        VStack {
            Text("Count: \\(count)")
            Button("Increment") { count += 1 }
        }
    }
}''',
        "kotlin": '''class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val button = findViewById<Button>(R.id.button)
        button.setOnClickListener { 
            Toast.makeText(this, "Clicked!", Toast.LENGTH_SHORT).show()
        }
    }
}'''
    }
}


def generate_sandbox_code(topic: str, language: str = "python") -> str:
    """
    Generate quick-start code for a given topic and language.
    
    Args:
        topic: Topic (e.g., "API Design", "Authentication")
        language: Programming language (python, javascript, etc.)
    
    Returns:
        10-line starter code template
    """
    if topic not in SANDBOX_TEMPLATES:
        return f"# {topic} starter template not available\n# Please refer to official documentation"
    
    templates = SANDBOX_TEMPLATES[topic]
    
    # Fallback to first available language if requested not found
    if language not in templates:
        language = list(templates.keys())[0]
    
    return templates[language]


def get_available_languages(topic: str) -> list[str]:
    """Get available languages for a topic."""
    return list(SANDBOX_TEMPLATES.get(topic, {}).keys())


def get_all_topics() -> list[str]:
    """Get all topics with sandbox templates."""
    return list(SANDBOX_TEMPLATES.keys())


def format_sandbox_markdown(topic: str, language: str = "python") -> str:
    """Format sandbox code as markdown code block."""
    code = generate_sandbox_code(topic, language)
    return f"```{language}\n{code}\n```"
