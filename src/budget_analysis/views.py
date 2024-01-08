from http import HTTPStatus

import requests
from django.conf import settings
from django.http import JsonResponse


def test_endpoint(request):
    res: requests.Response = requests.get(
        f"{settings.BUDGET_ANALYSIS_URL}/test", timeout=5
    )
    if res.status_code == 200:
        return JsonResponse(
            {"message": "correctly connected to the hfm-budget-analysis service"},
            status=HTTPStatus.OK,
        )
