from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import logging

from src.models.api_models import SupportRequest, SupportResponse
from src.services.agent import SupportAgent

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hiver Support Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = None

@app.on_event("startup")
async def startup_event():
    """I load the heavy ML models (like sentence-transformers) into memory on startup so the API responds instantly."""
    global agent
    logger.info("Initializing Support Agent...")
    try:
        agent = SupportAgent()
        logger.info("Agent initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """I built this to prevent leaking stack traces to the client in production."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.post("/support", response_model=SupportResponse)
async def handle_support_request(request: SupportRequest):
    """
    My main endpoint that takes a customer message and returns the AI's intent and decision.
    Validates input, processes through pipeline, returns decision and draft.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    if not agent:
        raise HTTPException(status_code=503, detail="Agent is not ready yet")
        
    try:
        logger.info(f"Processing request: {request.message[:50]}...")
        response = agent.process_request(request)
        logger.info(f"Decision: {response.decision}, Intent: {response.intent}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Error processing request")

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "agent_ready": agent is not None}

@app.get("/")
def read_root():
    """Redirects to the Swagger UI documentation."""
    return RedirectResponse(url="/docs")
