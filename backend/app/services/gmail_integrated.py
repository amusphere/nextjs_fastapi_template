"""
Gmail Integration Service

Service that provides email operations using Gmail API directly
Includes authentication, email sending/receiving, and label management features
"""

import base64
import email.mime.text
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from app.schema import User
from app.services.google_oauth import GoogleOauthService
from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlmodel import Session

logger = logging.getLogger(__name__)

# Gmail API related constants
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]
METADATA_HEADERS = ["From", "To", "Subject", "Date", "Cc", "Bcc"]
EMAIL_MIME_TYPES = ["text/plain", "text/html"]


class GmailServiceError(Exception):
    """Gmail service related error"""

    pass


class GmailAuthenticationError(GmailServiceError):
    """Gmail authentication related error"""

    pass


class GmailAPIError(GmailServiceError):
    """Gmail API call related error"""

    pass


class IntegratedGmailService:
    """
    Integrated service that uses Gmail API directly

    Provides features like email list retrieval, sending, label management
    Can be used as a context manager
    """

    def __init__(self, user: Optional[User] = None, session: Optional[Session] = None):
        self.user = user
        self.db_session = session
        self.gmail_service = None
        self._credentials: Optional[OAuth2Credentials] = None
        self._is_connected = False

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if Gmail service is connected"""
        return self._is_connected and self.gmail_service is not None

    async def connect(self) -> None:
        """Connect to Gmail API service"""
        if self._is_connected:
            logger.debug("Already connected to Gmail API")
            return

        try:
            logger.info("Connecting to Gmail API...")

            if self.user and self.db_session:
                await self._setup_credentials()
                self.gmail_service = build("gmail", "v1", credentials=self._credentials)

            self._is_connected = True
            logger.info("Successfully connected to Gmail API")

        except Exception as e:
            logger.error(f"Failed to connect to Gmail API: {e}")
            raise GmailServiceError(f"Connection error: {e}")

    async def _setup_credentials(self) -> None:
        """Set up Google OAuth credentials"""
        if not self.user or not self.db_session:
            raise GmailAuthenticationError(
                "User information or session information is missing"
            )

        try:
            oauth_service = GoogleOauthService(self.db_session)
            credentials = oauth_service.get_credentials(self.user.id)

            if not credentials:
                raise GmailAuthenticationError(
                    "Google credentials not found. Re-authentication is required."
                )

            # Build OAuth2Credentials object
            self._credentials = OAuth2Credentials(
                token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                scopes=GMAIL_SCOPES,
            )

            logger.debug("Google OAuth credentials have been set")

        except Exception as e:
            logger.error(f"Authentication setup error: {e}")
            raise GmailAuthenticationError(f"Failed to set up authentication: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Gmail API service"""
        self.gmail_service = None
        self._credentials = None
        self._is_connected = False
        logger.debug("Disconnected from Gmail API")

    def _ensure_connected(self) -> None:
        """Check connection status and raise exception if not connected"""
        if not self.is_connected:
            raise GmailServiceError("Not connected to Gmail service")

    # Gmail operation methods

    async def get_emails(
        self, query: str = "", max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve email list

        Args:
            query: Search query (Gmail search syntax)
            max_results: Maximum number of emails to retrieve

        Returns:
            Email list (including metadata)
        """
        self._ensure_connected()

        try:
            # Get message list
            result = (
                self.gmail_service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = result.get("messages", [])
            if not messages:
                return []

            # Get details for each message in parallel
            email_list = []
            for message in messages:
                email_data = await self._get_message_metadata(message["id"])
                email_list.append(email_data)

            return email_list

        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise GmailAPIError(f"Failed to retrieve emails: {e}")
        except Exception as e:
            logger.error(f"Email retrieval error: {e}")
            raise GmailServiceError(f"Failed to retrieve emails: {e}")

    async def _get_message_metadata(self, message_id: str) -> Dict[str, Any]:
        """Get message metadata"""
        msg = (
            self.gmail_service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=METADATA_HEADERS,
            )
            .execute()
        )

        # Organize metadata
        headers = msg["payload"].get("headers", [])
        email_data = {
            "id": msg["id"],
            "threadId": msg["threadId"],
            "snippet": msg.get("snippet", ""),
        }

        # Extract header information
        for header in headers:
            name = header["name"].lower()
            if name in ["from", "to", "subject", "date", "cc", "bcc"]:
                email_data[name] = header["value"]

        return email_data

    async def get_email_content(self, email_id: str) -> Dict[str, Any]:
        """
        Get specific email content

        Args:
            email_id: Email ID

        Returns:
            Email content (including body)
        """
        self._ensure_connected()

        try:
            msg = (
                self.gmail_service.users()
                .messages()
                .get(userId="me", id=email_id, format="full")
                .execute()
            )

            # Extract message body
            body = self._extract_message_body(msg["payload"])

            # Extract header information
            headers = msg["payload"].get("headers", [])
            email_data = {
                "id": msg["id"],
                "threadId": msg["threadId"],
                "body": body,
                "snippet": msg.get("snippet", ""),
            }

            # Parse header information
            for header in headers:
                name = header["name"].lower()
                if name in ["from", "to", "subject", "date", "cc", "bcc"]:
                    email_data[name] = header["value"]

            return email_data

        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise GmailAPIError(f"Failed to get email content: {e}")
        except Exception as e:
            logger.error(f"Email content retrieval error: {e}")
            raise GmailServiceError(f"Failed to get email content: {e}")

    def _extract_message_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract message body from message payload

        Prioritizes plain text, uses HTML as fallback
        """
        body = ""

        def decode_data(data: str) -> str:
            """Decode Base64 data"""
            try:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            except Exception as e:
                logger.warning(f"Message decode error: {e}")
                return ""

        if "parts" in payload:
            # For multipart messages
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                data = part["body"].get("data")

                if data:
                    if mime_type == "text/plain":
                        body = decode_data(data)
                        break  # Prioritize plain text
                    elif mime_type == "text/html" and not body:
                        body = decode_data(data)
        else:
            # For simple messages
            mime_type = payload.get("mimeType", "")
            if mime_type in EMAIL_MIME_TYPES:
                data = payload["body"].get("data")
                if data:
                    body = decode_data(data)

        return body

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send email

        Args:
            to: Destination email address
            subject: Subject
            body: Message body
            cc: CC email address (optional)
            bcc: BCC email address (optional)

        Returns:
            Send result
        """
        self._ensure_connected()

        try:
            raw_message = self._create_message(to, subject, body, cc, bcc)

            # Send email
            result = (
                self.gmail_service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            return {
                "id": result["id"],
                "threadId": result["threadId"],
                "status": "sent",
            }

        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise GmailAPIError(f"Failed to send email: {e}")
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            raise GmailServiceError(f"Failed to send email: {e}")

    async def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create draft

        Args:
            to: Destination email address
            subject: Subject
            body: Message body
            cc: CC email address (optional)
            bcc: BCC email address (optional)

        Returns:
            Draft creation result
        """
        self._ensure_connected()

        try:
            raw_message = self._create_message(to, subject, body, cc, bcc)

            # Create draft
            result = (
                self.gmail_service.users()
                .drafts()
                .create(userId="me", body={"message": {"raw": raw_message}})
                .execute()
            )

            return {
                "id": result["id"],
                "message": result["message"],
                "status": "draft_created",
            }

        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise GmailAPIError(f"Failed to create draft: {e}")
        except Exception as e:
            logger.error(f"Draft creation error: {e}")
            raise GmailServiceError(f"Failed to create draft: {e}")

    def _create_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> str:
        """
        Create email message and encode it to Base64

        Returns:
            Base64 encoded message
        """
        message = email.mime.text.MIMEText(body, "plain", "utf-8")
        message["to"] = to
        message["subject"] = subject

        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc

        # Base64 encoding
        return base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    # Label operation methods

    async def mark_as_read(self, email_id: str) -> Dict[str, Any]:
        """
        Mark email as read

        Args:
            email_id: Email ID

        Returns:
            Operation result
        """
        return await self._modify_labels(email_id, remove_labels=["UNREAD"])

    async def mark_as_unread(self, email_id: str) -> Dict[str, Any]:
        """
        Mark email as unread

        Args:
            email_id: Email ID

        Returns:
            Operation result
        """
        return await self._modify_labels(email_id, add_labels=["UNREAD"])

    async def _modify_labels(
        self,
        email_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Modify email labels

        Args:
            email_id: Email ID
            add_labels: List of labels to add
            remove_labels: List of labels to remove

        Returns:
            Operation result
        """
        self._ensure_connected()

        try:
            body = {}
            if add_labels:
                body["addLabelIds"] = add_labels
            if remove_labels:
                body["removeLabelIds"] = remove_labels

            result = (
                self.gmail_service.users()
                .messages()
                .modify(userId="me", id=email_id, body=body)
                .execute()
            )

            # Determine operation content
            status = "labels_modified"
            if remove_labels and "UNREAD" in remove_labels:
                status = "marked_as_read"
            elif add_labels and "UNREAD" in add_labels:
                status = "marked_as_unread"

            return {"id": result["id"], "status": status}

        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise GmailAPIError(f"Failed to modify labels: {e}")
        except Exception as e:
            logger.error(f"Label operation error: {e}")
            raise GmailServiceError(f"Failed to modify labels: {e}")


# Factory functions and helper functions


@asynccontextmanager
async def get_integrated_gmail_service(
    user: Optional[User] = None, session: Optional[Session] = None
):
    """
    IntegratedGmailService context manager

    Args:
        user: User information (required if authentication is needed)
        session: Database session

    Yields:
        IntegratedGmailService: Gmail service instance
    """
    service = IntegratedGmailService(user=user, session=session)
    try:
        async with service:
            yield service
    except Exception as e:
        logger.error(f"Gmail service error: {e}")
        raise


@asynccontextmanager
async def get_authenticated_gmail_service(user: User, session: Session):
    """
    Authenticated IntegratedGmailService context manager

    Args:
        user: User information (required)
        session: Database session (required)

    Yields:
        IntegratedGmailService: Authenticated Gmail service instance
    """
    if not user:
        raise GmailAuthenticationError("User information is required")
    if not session:
        raise GmailServiceError("Database session is required")

    async with get_integrated_gmail_service(user=user, session=session) as service:
        yield service
