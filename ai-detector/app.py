"""
AI-Powered Semantic Detection Service for Wozway
Provides intelligent detection beyond regex patterns
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import ollama
import re
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI(title="Wozway AI Detector")

# Load models on startup
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, 80MB

# Known malicious prompt embeddings (pre-computed)
MALICIOUS_EMBEDDINGS = []  # Load from database

class AnalyzeRequest(BaseModel):
    text: str
    checks: List[str] = ["pii", "prompt_injection", "toxicity"]
    threshold: float = 0.7

class Violation(BaseModel):
    type: str
    confidence: float
    explanation: str
    matched_text: Optional[str] = None

class AnalyzeResponse(BaseModel):
    violation: bool
    violations: List[Violation]
    processing_time_ms: float

# Semantic PII Detection
def detect_semantic_pii(text: str) -> List[Violation]:
    """Detect obfuscated or contextual PII"""
    violations = []
    
    # Use Ollama for semantic understanding
    prompt = f"""Analyze this text for personal information (PII) including obfuscated forms.
Look for: SSN, credit cards, phone numbers, addresses, even if written as words or with substitutions.

Text: "{text}"

Respond with JSON: {{"has_pii": true/false, "type": "SSN/CC/Phone/etc", "confidence": 0-1}}"""
    
    try:
        response = ollama.chat(
            model='llama3.2:1b',  # Fast, small model
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0}  # Deterministic
        )
        
        # Parse response
        result = parse_llm_response(response['message']['content'])
        
        if result.get('has_pii') and result.get('confidence', 0) > 0.7:
            violations.append(Violation(
                type=f"PII_{result['type']}",
                confidence=result['confidence'],
                explanation=f"Detected {result['type']} in semantic analysis"
            ))
    except Exception as e:
        print(f"Ollama error: {e}")
    
    return violations

# Prompt Injection Detection
def detect_prompt_injection(text: str) -> List[Violation]:
    """Detect prompt injection attempts"""
    violations = []
    
    # Pattern-based detection (fast)
    injection_patterns = [
        r"ignore\s+(previous|above|prior)\s+instructions",
        r"disregard\s+.*\s+rules",
        r"you\s+are\s+now\s+(in\s+)?DAN\s+mode",
        r"pretend\s+you\s+are",
        r"system\s*:\s*",
        r"<\|im_start\|>",  # Token injection
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(Violation(
                type="PROMPT_INJECTION",
                confidence=0.9,
                explanation="Pattern-based injection detected",
                matched_text=re.search(pattern, text, re.IGNORECASE).group()
            ))
            return violations
    
    # Embedding similarity (catches novel attacks)
    text_embedding = embedding_model.encode(text)
    
    for known_attack_embedding in MALICIOUS_EMBEDDINGS:
        similarity = cosine_similarity(text_embedding, known_attack_embedding)
        if similarity > 0.85:
            violations.append(Violation(
                type="PROMPT_INJECTION",
                confidence=similarity,
                explanation="Similar to known injection attack"
            ))
            break
    
    return violations

# Toxicity Detection
def detect_toxicity(text: str) -> List[Violation]:
    """Detect toxic, harmful, or biased content"""
    violations = []
    
    # Use Ollama for nuanced detection
    prompt = f"""Rate this text for toxicity, hate speech, harassment, or harmful content.
Consider context and intent.

Text: "{text}"

Respond with JSON: {{"is_toxic": true/false, "category": "hate/harassment/violence/none", "severity": 0-1}}"""
    
    try:
        response = ollama.chat(
            model='llama3.2:1b',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0}
        )
        
        result = parse_llm_response(response['message']['content'])
        
        if result.get('is_toxic') and result.get('severity', 0) > 0.6:
            violations.append(Violation(
                type=f"TOXICITY_{result['category'].upper()}",
                confidence=result['severity'],
                explanation=f"Detected {result['category']} content"
            ))
    except Exception as e:
        print(f"Toxicity check error: {e}")
    
    return violations

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def parse_llm_response(text: str) -> Dict:
    """Parse JSON from LLM response"""
    import json
    try:
        # Extract JSON from markdown code blocks if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        return json.loads(text.strip())
    except:
        return {}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """Main endpoint for semantic analysis"""
    import time
    start = time.time()
    
    all_violations = []
    
    # Run requested checks
    if "pii" in request.checks:
        all_violations.extend(detect_semantic_pii(request.text))
    
    if "prompt_injection" in request.checks:
        all_violations.extend(detect_prompt_injection(request.text))
    
    if "toxicity" in request.checks:
        all_violations.extend(detect_toxicity(request.text))
    
    # Filter by threshold
    filtered_violations = [
        v for v in all_violations 
        if v.confidence >= request.threshold
    ]
    
    processing_time = (time.time() - start) * 1000
    
    return AnalyzeResponse(
        violation=len(filtered_violations) > 0,
        violations=filtered_violations,
        processing_time_ms=processing_time
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": "llama3.2:1b"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
