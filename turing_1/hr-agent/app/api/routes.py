from fastapi import APIRouter, HTTPException, Request
from auth.oauth2_service import get_user_from_session
from hr_functions.leave import get_leave_balance
from hr_functions.capex import get_team_capex
from hr_functions.org import get_org_members
from llm.ollama_client import chat
from app.rag.rag_service import get_relevant_context

router = APIRouter()

# Endpoint: Main HR Agent - handles HR queries and routes to appropriate service
# Requires: User to be authenticated via Keycloak OAuth2 (session-based)
@router.post("/v1/completions")
def hr_agent(request: dict, request_obj: Request):
    # Get user from Keycloak session
    user = get_user_from_session(request_obj)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated. Please login via Keycloak first.")

    # Get user ID and parse user query
    uid = user.get("uid") or user.get("sub") or user.get("email")
    prompt = request["prompt"].lower()

    # Route to appropriate HR function based on keyword matching
    if "leave" in prompt:
        return {"response": get_leave_balance(uid)}

    elif "capex" in prompt:
        return {"response": get_team_capex(uid)}

    elif "team" in prompt or "organization" in prompt:
        return {"response": get_org_members(uid)}

    else:
        # Use RAG to fetch relevant company docs and augment prompt
        context_docs = get_relevant_context(prompt, top_k=3)
        if context_docs:
            augmented = "\n\n".join(context_docs) + "\n\nUser question: " + prompt
        else:
            augmented = prompt
        # Use Ollama LLM for general queries with context
        return {"response": chat(augmented)}
