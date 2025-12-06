import os
import sys
import datetime
import argparse
import csv
from typing import List, Dict, Optional, Any

# Third-party libraries for Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# SCOPES define the level of access.
# We only need read access for an exporter.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Export Google Calendar events to a CSV file."
    )
    
    parser.add_argument(
        '--start-date', 
        type=str, 
        help='Start date in YYYY-MM-DD format. Defaults to today.'
    )
    parser.add_argument(
        '--end-date', 
        type=str, 
        help='End date in YYYY-MM-DD format. Defaults to 7 days from start.'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='events.csv', 
        help='Output CSV filename. Defaults to "events.csv".'
    )
    parser.add_argument(
        '--max-results', 
        type=int, 
        default=2500, 
        help='Maximum number of events to fetch. Defaults to 2500.'
    )
    parser.add_argument(
        '--calendar-id', 
        type=str, 
        default='primary', 
        help='The ID of the calendar to export. Defaults to "primary".'
    )
    parser.add_argument(
        '--credentials',
        type=str,
        default='credentials.json',
        help='Path to the Google Cloud credentials.json file.'
    )

    return parser.parse_args()

def authenticate_google_calendar(creds_file: str):
    """
    Handles OAuth2 authentication flow.
    Creates/Loads 'token.json' for persistent login.
    """
    creds = None
    token_file = 'token.json'

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print(f"Warning: Corrupt token file. Re-authenticating. ({e})")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                print("Token expired and refresh failed. Deleting token.json and restarting flow.")
                if os.path.exists(token_file):
                    os.remove(token_file)
                return authenticate_google_calendar(creds_file)
        else:
            if not os.path.exists(creds_file):
                print(f"Error: '{creds_file}' not found.")
                print("Please download your OAuth 2.0 Client ID JSON from Google Cloud Console.")
                sys.exit(1)
                
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return creds

def format_iso_date(date_str: Optional[str], days_offset: int = 0) -> str:
    """
    Converts YYYY-MM-DD string to RFC3339 format (ISO 8601) with 'Z' (UTC).
    If date_str is None, uses current time + offset.
    """
    if date_str:
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD.")
            sys.exit(1)
    else:
        dt = datetime.datetime.utcnow() + datetime.timedelta(days=days_offset)
    
    # API expects format: 2023-01-01T00:00:00Z
    return dt.isoformat() + 'Z' 

def parse_event_time(event_date_obj: Dict[str, Any]) -> str:
    """
    Helper to extract a clean string from Google's date object.
    Handles 'dateTime' (specific time) vs 'date' (all-day events).
    """
    if 'dateTime' in event_date_obj:
        return event_date_obj['dateTime']
    elif 'date' in event_date_obj:
        return f"{event_date_obj['date']} (All Day)"
    return "Unknown"

def fetch_events(service, calendar_id: str, start_iso: str, end_iso: str, max_total: int) -> List[Dict]:
    """Fetches events from the API, handling pagination automatically."""
    events_result = []
    page_token = None

    print(f"Fetching events from {start_iso} to {end_iso}...")

    while True:
        try:
            # Fetch a page of events
            events_list_request = service.events().list(
                calendarId=calendar_id,
                timeMin=start_iso,
                timeMax=end_iso,
                maxResults=min(500, max_total - len(events_result)), # Fetch chunks of 500
                singleEvents=True,
                orderBy='startTime',
                pageToken=page_token
            )
            current_page = events_list_request.execute()
            
            events = current_page.get('items', [])
            events_result.extend(events)
            
            page_token = current_page.get('nextPageToken')
            
            # Stop if no more pages or we hit the user-defined limit
            if not page_token or len(events_result) >= max_total:
                break

        except HttpError as error:
            print(f"An API error occurred: {error}")
            sys.exit(1)

    return events_result[:max_total]

def save_to_csv(events: List[Dict], filename: str):
    """Writes the list of event dictionaries to a CSV file."""
    if not events:
        print("No events found in the specified range.")
        return

    # Define the columns we want in the CSV
    fieldnames = ['Summary', 'Start Time', 'End Time', 'Description', 'Location', 'Link']

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for event in events:
                # Extract and clean data
                row = {
                    'Summary': event.get('summary', 'No Title'),
                    'Start Time': parse_event_time(event.get('start', {})),
                    'End Time': parse_event_time(event.get('end', {})),
                    'Description': event.get('description', '').replace('\n', ' '), # Flatten newlines
                    'Location': event.get('location', ''),
                    'Link': event.get('htmlLink', '')
                }
                writer.writerow(row)
        
        print(f"Successfully exported {len(events)} events to '{filename}'.")

    except IOError as e:
        print(f"Error writing to file '{filename}': {e}")

def main():
    args = parse_arguments()

    # 1. Authenticate
    creds = authenticate_google_calendar(args.credentials)
    service = build('calendar', 'v3', credentials=creds)

    # 2. Prepare Dates
    # If start is missing, default to now.
    # If end is missing, default to start + 7 days.
    start_iso = format_iso_date(args.start_date)
    
    if args.end_date:
        end_iso = format_iso_date(args.end_date)
    else:
        # Default logic: if start date was user-provided, add 7 days to that.
        # If start date was auto-now, add 7 days to now.
        base_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else datetime.datetime.utcnow()
        end_dt = base_date + datetime.timedelta(days=7)
        end_iso = end_dt.isoformat() + 'Z'

    # 3. Fetch Data
    events = fetch_events(service, args.calendar_id, start_iso, end_iso, args.max_results)

    # 4. Export
    save_to_csv(events, args.output)

if __name__ == '__main__':
    main()