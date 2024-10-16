from django.http import JsonResponse
def SendJson(data = {}, status = 200, message = ""):
    return JsonResponse({
        'status': status,
        'message': message,
        'data': data
    }, status=status)
