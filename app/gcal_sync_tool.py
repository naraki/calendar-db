#!/usr/bin/env python3
"""
Google Calendar to MySQL Sync CLI
Author: Automation Engineer
Description: Synchronizes Google Calendar events to a local MySQL database.
"""

import os
import sys
import argparse
import datetime
import logging
from typing import Optional, List, Dict, Any

# Third-party libraries
import mysql.connector
from mysql.connector import Error as MySQLError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE = 'token.json'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class CalendarDBSync:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.creds = None
        self.service = None
        self.db_conn = None
        self.cursor = None

    def authenticate_google(self) -> None:
        """Handles the OAuth2 flow for Google API."""
        try:
            if os.path.exists(TOKEN_FILE):
                self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.args.credentials):
                        logger.error(f"Credentials file '{self.args.credentials}' not found.")
                        sys.exit(1)
                        
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.args.credentials, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(TOKEN_FILE, 'w') as token:
                    token.write(self.creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=self.creds)
            logger.info("Google Authentication successful.")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            sys.exit(1)

    def connect_db(self) -> None:
        """Establishes connection to MySQL database."""
        try:
            self.db_conn = mysql.connector.connect(
                host=self.args.host,
                user=self.args.user,
                password=self.args.password,
                database=self.args.db,
                port=self.args.port
            )
            self.cursor = self.db_conn.cursor()
            logger.info(f"Connected to MySQL Database: {self.args.db}")
        except MySQLError as e:
            logger.error(f"Database connection failed: {e}")
            sys.exit(1)

    def init_db_schema(self) -> None:
        """Creates the events table if it does not exist."""
        table_schema = """
        CREATE TABLE IF NOT EXISTS events (
            id VARCHAR(255) PRIMARY KEY,
            summary VARCHAR(255),
            description TEXT,
            location VARCHAR(255),
            start_time DATETIME,
            end_time DATETIME,
            html_link VARCHAR(512),
            status VARCHAR(50),
            created_at DATETIME,
            updated_at DATETIME,
            last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        try:
            self.cursor.execute(table_schema)
            self.db_conn.commit()
            logger.info("Database schema verified/created.")
        except MySQLError as e:
            logger.error(f"Failed to initialize schema: {e}")
            sys.exit(1)

    def _parse_iso_datetime(self, date_str: str) -> Optional[str]:
        """Parses Google ISO format to MySQL DATETIME format."""
        if not date_str:
            return None
        # Google returns RFC3339; Python < 3.11 handles it strictly, 
        # but string slicing is a robust way to strip timezone for MySQL DATETIME
        # Example: 2023-10-27T10:00:00-05:00 -> 2023-10-27 10:00:00
        try:
            # Handle 'date' only (all day events) e.g. "2023-10-27"
            if len(date_str) == 10: 
                return f"{date_str} 00:00:00"
            
            dt = datetime.datetime.fromisoformat(date_str)
            # Convert to UTC or keep naive? Here we strip TZ info for MySQL DATETIME compatibility
            # Ideally MySQL columns should be TIMESTAMP if TZ awareness is critical.
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

    def fetch_events(self) -> List[Dict[str, Any]]:
        """Fetches upcoming events from Google Calendar."""
        logger.info(f"Fetching max {self.args.max_results} events...")
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        events_result = self.service.events().list(
            calendarId='primary', 
            timeMin=now,
            maxResults=self.args.max_results, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        logger.info(f"Retrieved {len(events)} events from Google API.")
        return events

    def upsert_event(self, event: Dict[str, Any]) -> None:
        """Inserts or Updates an event in MySQL."""
        
        # Extract fields
        event_id = event.get('id')
        summary = event.get('summary', 'No Title')
        description = event.get('description', '')
        location = event.get('location', '')
        status = event.get('status', '')
        html_link = event.get('htmlLink', '')
        created_at = self._parse_iso_datetime(event.get('created'))
        updated_at = self._parse_iso_datetime(event.get('updated'))

        # Handle start/end (could be 'dateTime' or 'date' for all-day)
        start = event.get('start', {})
        end = event.get('end', {})
        start_time = self._parse_iso_datetime(start.get('dateTime', start.get('date')))
        end_time = self._parse_iso_datetime(end.get('dateTime', end.get('date')))

        sql = """
        INSERT INTO events 
        (id, summary, description, location, start_time, end_time, html_link, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            summary = VALUES(summary),
            description = VALUES(description),
            location = VALUES(location),
            start_time = VALUES(start_time),
            end_time = VALUES(end_time),
            html_link = VALUES(html_link),
            status = VALUES(status),
            updated_at = VALUES(updated_at);
        """

        val = (
            event_id, summary, description, location, 
            start_time, end_time, html_link, status, 
            created_at, updated_at
        )

        try:
            self.cursor.execute(sql, val)
        except MySQLError as e:
            logger.error(f"Error upserting event {event_id}: {e}")

    def run(self) -> None:
        """Main execution flow."""
        self.authenticate_google()
        self.connect_db()
        self.init_db_schema()
        
        events = self.fetch_events()
        
        if not events:
            logger.info("No upcoming events found.")
        else:
            count = 0
            for event in events:
                self.upsert_event(event)
                count += 1
            
            self.db_conn.commit()
            logger.info(f"Successfully synced {count} events to MySQL.")

        # Cleanup
        if self.db_conn.is_connected():
            self.cursor.close()
            self.db_conn.close()

def main():
    parser = argparse.ArgumentParser(description='Sync Google Calendar to MySQL.')
    
    # Database Arguments
    parser.add_argument('--host', required=True, help='MySQL Host')
    parser.add_argument('--user', required=True, help='MySQL User')
    parser.add_argument('--password', required=True, help='MySQL Password')
    parser.add_argument('--db', required=True, help='MySQL Database Name')
    parser.add_argument('--port', default=3306, type=int, help='MySQL Port (default: 3306)')
    
    # Google Config
    parser.add_argument('--credentials', default='credentials.json', help='Path to Google OAuth credentials.json')
    parser.add_argument('--max-results', default=100, type=int, help='Max events to fetch (default: 100)')

    args = parser.parse_args()

    syncer = CalendarDBSync(args)
    syncer.run()

if __name__ == '__main__':
    main()