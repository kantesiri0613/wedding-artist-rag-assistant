import json
import os
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_engine.answering import AnswerGenerator
from rag_engine.chunking import load_chunks
from rag_engine.retrieval import Retriever
from rag_engine.vectorbase import VectorBase

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")
DATA_FILE = ROOT / "data" / "live_painting_data.txt"
BOOKINGS_FILE = ROOT / "data" / "bookings.json"
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "live_painting_knowledge_v2"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "harshitaAdmin")


def normalize_identifier(value: str) -> str:
    return str(value or "").strip().lower()


def ensure_bookings_file() -> None:
    BOOKINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not BOOKINGS_FILE.exists():
        BOOKINGS_FILE.write_text("[]", encoding="utf-8")


def load_bookings() -> list[dict[str, Any]]:
    ensure_bookings_file()
    try:
        data = json.loads(BOOKINGS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_bookings(bookings: list[dict[str, Any]]) -> None:
    ensure_bookings_file()
    BOOKINGS_FILE.write_text(json.dumps(bookings, indent=2), encoding="utf-8")


def get_customer_matches(identifier: str, booking: dict[str, Any]) -> bool:
    raw = normalize_identifier(identifier)
    phone = normalize_identifier(str(booking.get("phone") or ""))
    email = normalize_identifier(str(booking.get("email") or ""))
    return raw and (raw == phone or raw == email or phone.startswith(raw) or email.startswith(raw))


vectorbase = VectorBase(CHROMA_DIR, COLLECTION_NAME)
INDEXED_CHUNKS = vectorbase.index(load_chunks(DATA_FILE), DATA_FILE.name)
retriever = Retriever(vectorbase)
answer_generator = AnswerGenerator()

app = FastAPI(title="AuraCanvas RAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

OTP_STORE: dict[str, str] = {}
SESSIONS: dict[str, dict[str, Any]] = {}


class ChatRequest(BaseModel):
    message: str


class RequestOTPRequest(BaseModel):
    identifier: str


class VerifyOTPRequest(BaseModel):
    identifier: str
    otp: str


class AdminLoginRequest(BaseModel):
    password: str


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "AuraCanvas RAG API",
        "health": "/health",
        "chat": "/chat",
        "auth": "/api/auth",
        "bookings": "/api/bookings",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "collection": COLLECTION_NAME, "chunks": INDEXED_CHUNKS}


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    message = request.message.strip()
    if not message:
        return {"answer": "Please enter a question about live event painting."}
    sources = retriever.retrieve(message)
    return {
        "answer": answer_generator.generate(message, sources),
        "sources": sources,
        "used_gemini": bool(os.getenv("GEMINI_API_KEY")),
    }


@app.post("/api/auth/request-otp")
def request_otp(request: RequestOTPRequest) -> dict[str, Any]:
    identifier = normalize_identifier(request.identifier)
    if not identifier:
        raise HTTPException(status_code=400, detail="Phone or email is required.")

    otp = "123456"
    OTP_STORE[identifier] = otp
    return {
        "success": True,
        "message": "Demo OTP generated successfully.",
        "demo_otp": otp,
        "identifier": identifier,
    }


@app.post("/api/auth/verify-otp")
def verify_otp(request: VerifyOTPRequest) -> dict[str, Any]:
    identifier = normalize_identifier(request.identifier)
    otp = str(request.otp).strip()
    if not identifier:
        raise HTTPException(status_code=400, detail="Phone or email is required.")
    if OTP_STORE.get(identifier) != otp:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP.")

    token = uuid.uuid4().hex
    SESSIONS[token] = {"type": "customer", "identifier": identifier}
    OTP_STORE.pop(identifier, None)
    return {"success": True, "token": token, "role": "customer", "identifier": identifier}


@app.post("/api/admin/login")
def admin_login(request: AdminLoginRequest) -> dict[str, Any]:
    if request.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password.")

    token = uuid.uuid4().hex
    SESSIONS[token] = {"type": "admin"}
    return {"success": True, "token": token, "role": "admin"}


@app.get("/api/bookings")
def get_bookings(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token.")

    token = authorization.replace("Bearer ", "", 1).strip()
    session = SESSIONS.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    bookings = load_bookings()
    if session["type"] == "customer":
        identifier = normalize_identifier(session.get("identifier", ""))
        filtered = [item for item in bookings if get_customer_matches(identifier, item)]
        return {"success": True, "role": "customer", "bookings": filtered}

    return {"success": True, "role": "admin", "bookings": bookings}


@app.post("/api/bookings")
def create_booking(request: dict[str, Any], authorization: str | None = Header(default=None)) -> dict[str, Any]:
    payload = request or {}
    phone = str(payload.get("phone") or "")
    email = str(payload.get("email") or "")
    if not phone and not email:
        raise HTTPException(status_code=400, detail="Booking must include phone or email.")

    session = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "", 1).strip()
        session = SESSIONS.get(token)
        if not session:
            raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    if session and session["type"] == "customer":
        identifier = normalize_identifier(session.get("identifier", ""))
        allowed_phone = normalize_identifier(phone)
        allowed_email = normalize_identifier(email)
        if identifier and not (identifier == allowed_phone or identifier == allowed_email):
            raise HTTPException(status_code=403, detail="You can only save bookings for your own customer identity.")

    bookings = load_bookings()
    item = {**payload}
    item.setdefault("status", "Confirmed")
    item.setdefault("createdAt", str(__import__("datetime").datetime.utcnow().isoformat()))
    item.setdefault("refCode", f"#HARSHITA-{uuid.uuid4().hex[:8].upper()}")
    bookings.insert(0, item)
    save_bookings(bookings)
    return {"success": True, "message": "Booking saved successfully.", "booking": item}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rag_server:app", host="127.0.0.1", port=8001, reload=False)
