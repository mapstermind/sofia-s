import logging
import os
import time
from typing import Any

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build # type: ignore[import-untyped]
from googleapiclient.errors import HttpError # type: ignore[import-untyped]

logger = logging.getLogger("form_responses")

# Simple in-memory cache
_cache: dict[str, dict[str, Any]] = {}


def get_credentials() -> service_account.Credentials | None:
    """Get Google service account credentials from environment variable."""
    credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS

    if not credentials_path or not os.path.exists(credentials_path):
        logger.error(f"Google credentials file not found: {credentials_path}")
        return None

    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=[
                "https://www.googleapis.com/auth/forms.responses.readonly",
                "https://www.googleapis.com/auth/forms.body.readonly",
            ],
        )
        return credentials
    except Exception as e:
        logger.error(f"Error loading Google credentials: {e}")
        return None


def get_forms_service() -> Any | None:
    """Build and return Google Forms API service."""
    credentials = get_credentials()
    if not credentials:
        return None

    try:
        service = build("forms", "v1", credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Error building Forms service: {e}")
        return None


def normalize_answer(answer: dict[str, Any]) -> Any:
    """Normalize different answer types to a consistent format."""
    if "textAnswers" in answer:
        # Text-based answers
        text_answers = answer["textAnswers"].get("answers", [])
        if len(text_answers) == 1:
            return text_answers[0].get("value", "")
        elif len(text_answers) > 1:
            return ", ".join([a.get("value", "") for a in text_answers])
        return ""

    elif "choiceAnswers" in answer:
        # Multiple choice answers
        choice_answers = answer["choiceAnswers"].get("answers", [])
        if len(choice_answers) == 1:
            return choice_answers[0].get("value", "")
        elif len(choice_answers) > 1:
            return ", ".join([a.get("value", "") for a in choice_answers])
        return ""

    elif "fileUploadAnswers" in answer:
        # File upload answers
        file_answers = answer["fileUploadAnswers"].get("answers", [])
        if file_answers:
            return ", ".join([f.get("fileName", "") for f in file_answers])
        return ""

    return ""


def get_cache_key() -> str:
    """Generate cache key for form responses."""
    form_id = settings.GOOGLE_FORM_ID
    return f"form_responses_{form_id}"


def is_cache_valid() -> bool:
    """Check if cache is still valid."""
    cache_key = get_cache_key()
    if cache_key not in _cache:
        return False

    cache_time = _cache[cache_key].get("timestamp", 0)
    ttl = settings.FORMS_CACHE_SECONDS
    return (time.time() - cache_time) < ttl


def fetch_form_responses() -> list[dict[str, Any]]:
    """
    Fetch Google Form responses and return normalized data.

    Returns:
        List of dictionaries with keys:
        - submitted_at: ISO timestamp of submission
        - respondent_email: Email if available
        - answers: Dict mapping question titles to answers
    """
    # Check cache first
    if is_cache_valid():
        logger.info("Returning cached form responses")
        return _cache[get_cache_key()]["data"]

    form_id = settings.GOOGLE_FORM_ID
    if not form_id:
        logger.error("GOOGLE_FORM_ID not configured")
        return []

    service = get_forms_service()
    if not service:
        logger.error("Failed to create Forms service")
        return []

    try:
        # Get form structure to map question IDs to titles
        form = service.forms().get(formId=form_id).execute()
        questions = {}

        for item in form.get("items", []):
            question_id = (
                item.get("questionItem", {}).get("question", {}).get("questionId")
            )
            title = item.get("title", "")
            if question_id and title:
                questions[question_id] = title

        # Get form responses
        responses = service.forms().responses().list(formId=form_id).execute()
        normalized_responses = []

        for response in responses.get("responses", []):
            # Get submission timestamp
            submitted_at = response.get("createTime", "")

            # Get respondent email if available
            respondent_email = response.get("respondentEmail", "")

            # Normalize answers
            answers = {}
            answer_data = response.get("answers", {})

            for question_id, answer in answer_data.items():
                question_title = questions.get(question_id, f"Question {question_id}")
                normalized_value = normalize_answer(answer)
                answers[question_title] = normalized_value

            normalized_responses.append(
                {
                    "submitted_at": submitted_at,
                    "respondent_email": respondent_email,
                    "answers": answers,
                }
            )

        # Cache the results
        cache_key = get_cache_key()
        _cache[cache_key] = {"data": normalized_responses, "timestamp": time.time()}

        logger.info(f"Successfully fetched {len(normalized_responses)} form responses")
        return normalized_responses

    except HttpError as e:
        logger.error(f"Google Forms API error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching form responses: {e}")
        return []
