import logging

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from .google_forms import fetch_form_responses

logger = logging.getLogger("form_responses")


def form_responses_view(request: HttpRequest) -> HttpResponse:
    """
    Display Google Form responses in an HTML table.

    URL: /forms/responses/
    """
    try:
        responses = fetch_form_responses()

        if not responses:
            # Handle case where no responses are available
            context = {
                "responses": [],
                "questions": [],
                "error": None,
                "form_id": settings.GOOGLE_FORM_ID,
            }
            return render(request, "form_responses/responses.html", context)

        # Extract all unique question titles from all responses
        all_questions = set()
        for response in responses:
            all_questions.update(response["answers"].keys())

        # Sort questions for consistent column order
        questions = sorted(list(all_questions))

        # Prepare responses with answers in the same order as questions
        prepared_responses = []
        for response in responses:
            prepared_response = {
                "submitted_at": response["submitted_at"],
                "respondent_email": response["respondent_email"],
                "answers_list": [response["answers"].get(q, "") for q in questions],
            }
            prepared_responses.append(prepared_response)

        context = {
            "responses": prepared_responses,
            "questions": questions,
            "error": None,
            "form_id": settings.GOOGLE_FORM_ID,
        }

        return render(request, "form_responses/responses.html", context)

    except Exception as e:
        logger.error(f"Error in form_responses_view: {e}")
        context = {
            "responses": [],
            "questions": [],
            "error": f"An error occurred while fetching form responses: {str(e)}",
            "form_id": settings.GOOGLE_FORM_ID,
        }
        return render(request, "form_responses/responses.html", context)
