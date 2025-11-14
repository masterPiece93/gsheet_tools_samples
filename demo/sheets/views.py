import json
import requests
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from typing import *
from django_gauth.utilities import check_gauth_authentication
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError as GoogleServiceHttpError
from google.auth.exceptions import RefreshError
from icecream import ic
from django.http import JsonResponse
from gsheet_tools import (
    UrlResolver, 
    prepare_dataframe,
    NameFormatter,
    check_sheet_origin,
    get_gid_sheets_data,
    SheetOrigins
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .forms import MyForm

# Exceptions
# ----------
class InvalidGSheetUrl(Exception):
    """
    There is expectation of following types of google url only :     
        - https://docs.google.com/spreadsheets/d/{GOOGLE-SHEET-RESOURCE-ID}/edit?gid={SHEET-GID}#gid=546508778
        - https://docs.google.com/spreadsheets/d/{GOOGLE-SHEET-RESOURCE-ID}/edit?usp=sharing
    [Exception]"""
    pass


class GoogleUnauthenticated(Exception):
    """
    Indicates the user is un-authenticated or
        session expiration
    [Exception]"""
    pass


class GoogleSpreadsheetServiceError(Exception):
    """
    Google Sheets error scenarios
    [Exception]"""
    def __init__(self, *args, erorr_details=None):
        self.erorr_details = erorr_details
        super().__init__(*args)


class GcsFileUploadError(Exception):
    """Error in uploading data to GCS
    [Exception]"""
    pass


class GoogleSpreadsheetProcessingError(Exception):
    """
    Issue in Parsing specific Google Sheets
    [Exception]"""
    pass


# ==
# UI
# ==
def home_view(request):
    """[Sheets Landing Page]"""
    __title__ = "Sheets"
    return render(request, 'home.html', {"page_name": __title__})

def read_sheet_view(request):
    """[Reading Sheet Demo page]"""
    __title__ = "Read Sheet Demo"
    if request.method == "POST":
        form = MyForm(request.POST)
        if form.is_valid():
            # fetch clean form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            file_url = form.cleaned_data['file_url']
            # process the cleaned data
            # # making the api call for with fetched data .
            # # ( this could also have been don in JavaScript side )
            url = request.build_absolute_uri(reverse('sheets:read_sheet_api_controller'))
            session_id = request.COOKIES.get("sessionid")
            body = {"file_url": file_url}
            response = requests.post(url, json=body, cookies={"sessionid": session_id})
            ic(response.status_code) # :log
            ic(response.text)        # :log
            # # checking api response
            if response.status_code == 200:
                messages.success(request, 'Form submitted successfully!')
                data = response.json() # api response
                # # refresh page with information in session
                # # ( you can cache in localstorage as well if doing in JavaScript )
                request.session['submitted_data']={'name': name, 'email': email, 'file_url': file_url,"message": data["message"],"is_success": True}
                return redirect(reverse('sheets:read_sheet_view'))
            else:
                # Handle error
                messages.error(request, 'Form submission has errors!')
                if response.status_code == 401:
                    data = response.json()
                    # # stay on same page and show error from api response
                    return render(request, 'sheet_view.html', {'submitted_data': {'name': name, 'email': email, 'file_url': file_url, "message": data["error"],"is_success": False}, 'form': form}|{"page_name": __title__})
    else:
        form = MyForm()
    
    context = {'form': form} | {"page_name": __title__}
    if submitted_data:=request.session.get('submitted_data'):
        context['submitted_data']=submitted_data
        del request.session['submitted_data']
    return render(request, "sheet_view.html", context)

# ===
# API
# ===
@csrf_exempt
def read_sheet_api_controller(request):

    if request.method == "POST":
        return read_sheet_api(request)
    return HttpResponse("Not Implemented", status=501)

def read_sheet_api(request):
    try:    # body parsing
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        # Access data like: body_data['key']
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    file_url = "https://docs.google.com/spreadsheets/d/1XZ9QFJKZKit6O1rWYcpMdpNLXgAO7mn_vnAGrRGR7qQ/edit?usp=sharing"
    try:    # field validation
        file_url = body_data["file_url"]
    except KeyError:
        return JsonResponse({'error': 'Key `file_url` Required'}, status=400)
    
    url: UrlResolver = UrlResolver(file_url)
    if not url.is_valid:
        raise InvalidGSheetUrl("`google_sheet_url` is invalid.")
    is_authenticated, credentials = check_gauth_authentication(request.session)
    if not is_authenticated:
        raise GoogleUnauthenticated("google Oauth UnAuthenticated")
    google_sheet = build("sheets", "v4", credentials=credentials)
    google_drive = build('drive', 'v3', credentials=credentials)
    try:
        sheet_service: object = google_sheet.spreadsheets()
        file_id = url.url_data.file_id
        gid = url.url_data.gid or None
        origin, details = check_sheet_origin(google_drive, file_id)
        if origin == SheetOrigins.UPLOADED_NON_CONVERTED:
            error_msg = f"sheet not parsable as it is not correct google sheet."
            error_details = {
                "code": origin,
                "details": details._asdict()
            }
            raise GoogleSpreadsheetServiceError(error_msg, erorr_details=error_details)
        spreadsheet_metadata = sheet_service.get(
            spreadsheetId=file_id,
            fields='properties.title'
        ).execute()
        spreadsheet_name = spreadsheet_metadata.get('properties', {}).get('title')
        name, spreadsheet_data = get_gid_sheets_data(sheet_service, file_id, gid, without_headers=False)
        print(spreadsheet_data)
    except GoogleServiceHttpError as error:
        error_msg = str(error.status_code) + str(error.error_details)
        if error.status_code == 403:
            error_msg = "PERMISSION_DENIED : user does not have permission on this resource to access (read/edit/comment)."
        error_details = {
            "google_error_details": error.error_details,
            "google_reason": error.reason,
            "status_code": error.status_code,
            "uri": error.uri
        }
        raise GoogleSpreadsheetServiceError(error_msg, erorr_details=error_details)
    except RefreshError as e:
        raise GoogleUnauthenticated(str(e))
    else:
        
        filename: str = f"{NameFormatter.to_snake_case(spreadsheet_name)}__{NameFormatter.to_snake_case(name)}.csv"
        msg = f"Spreadsheet Name: {spreadsheet_name}, Indivisual Sheet Name: {name}, Formulated File Name : {filename}"
        ic(msg)
        ic(spreadsheet_data)
        spreadsheet_dataframe = prepare_dataframe(spreadsheet_data)
        msg = f"Prepared speadsheet dataframe successfully"
        ic(msg)
        return JsonResponse({'message': 'Successfully Prepared the dataframe'})
