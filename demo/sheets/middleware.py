from django.http import HttpResponseServerError, JsonResponse
from .views import GoogleUnauthenticated, GoogleSpreadsheetServiceError


class GlobalExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Log the exception
        print(f"Global middleware caught exception: {exception}")

        if isinstance(exception, GoogleUnauthenticated):
            return JsonResponse({"error": str(exception)}, status=401)
        elif isinstance(exception, GoogleSpreadsheetServiceError):
            print({"error": str(exception), "details": exception.erorr_details})
            return JsonResponse({"error": str(exception), "details": exception.erorr_details}, status=400)
        else:
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)
        # Return a custom error response
        return HttpResponseServerError("An unexpected server error occurred.")
