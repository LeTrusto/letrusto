from email.message import EmailMessage
from pathlib import Path
import base64
import json
import logging
import os
import secrets
import threading
from urllib.parse import urlparse

GMAIL_SEND_SCOPE = 'https://www.googleapis.com/auth/gmail.send'
SCOPES = [GMAIL_SEND_SCOPE, 'openid', 'email']
EMAIL_IDENTITY_SCOPE = 'https://www.googleapis.com/auth/userinfo.email'
EXPECTED_ACCOUNT = 'hello@letrusto.com'
OAUTH_CALLBACK_PATH = '/gmail/oauth2callback'
DEFAULT_CALLBACK_HOST = '127.0.0.1'
_pending_flows: dict[str, object] = {}
_flow_lock = threading.Lock()
logger = logging.getLogger(__name__)


class GmailOAuthError(RuntimeError):
    pass


def _scope_string(scopes) -> str:
    return ' '.join(sorted(set(scopes or [])))


def _required_scopes_present(scopes) -> bool:
    granted = set(scopes or [])
    return GMAIL_SEND_SCOPE in granted and 'openid' in granted and ('email' in granted or EMAIL_IDENTITY_SCOPE in granted)


def callback_uri_for_request(request=None, configured_uri: str | None = None) -> str:
    value = configured_uri or os.getenv('GMAIL_OAUTH_REDIRECT_URI')
    if not value and request is not None:
        scheme = request.url.scheme
        host = 'localhost'
        port = request.url.port
        value = f'{scheme}://{host}{f":{port}" if port else ""}{OAUTH_CALLBACK_PATH}'
    if not value:
        raise GmailOAuthError('GMAIL_OAUTH_REDIRECT_URI is not set and the callback address is unavailable.')
    parsed = urlparse(value)
    if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost', '::1'} or parsed.path != OAUTH_CALLBACK_PATH or parsed.query or parsed.fragment:
        raise GmailOAuthError('Gmail OAuth redirect URI must be an HTTP localhost callback ending in /gmail/oauth2callback.')
    return value


class GmailOAuth:
    def __init__(self, credentials_file: str | None = None, token_file: str | None = None, flow_factory=None, redirect_uri: str | None = None):
        credentials_value = credentials_file or os.getenv('GMAIL_CREDENTIALS_FILE')
        token_value = token_file or os.getenv('GMAIL_TOKEN_FILE')
        self.credentials_file = Path(credentials_value).expanduser() if credentials_value else None
        self.token_file = Path(token_value).expanduser() if token_value else None
        self.flow_factory = flow_factory
        self.redirect_uri = redirect_uri

    def _require_paths(self) -> tuple[Path, Path]:
        if not self.credentials_file:
            raise GmailOAuthError('GMAIL_CREDENTIALS_FILE is not set. Set it to the downloaded Google client JSON.')
        if not self.token_file:
            raise GmailOAuthError('GMAIL_TOKEN_FILE is not set. Set it to a private token path.')
        if not self.credentials_file.is_file():
            raise GmailOAuthError(f'Google credentials file was not found: {self.credentials_file}')
        return self.credentials_file, self.token_file

    def _token_path_warning(self) -> str:
        if not self.token_file:
            return ''
        repository_root = Path(__file__).resolve().parents[2]
        try:
            self.token_file.resolve().relative_to(repository_root)
            return 'Token path is inside the leadgen repository; move it outside the repository.'
        except ValueError:
            return ''

    def _load_google(self):
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google.oauth2 import id_token
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError as exc:
            raise GmailOAuthError('Install google-auth-oauthlib and google-api-python-client first.') from exc
        return Request, Credentials, id_token, InstalledAppFlow

    def _client_id(self) -> str:
        credentials_file, _ = self._require_paths()
        data = json.loads(credentials_file.read_text(encoding='utf-8'))
        client = data.get('installed') or data.get('web') or {}
        client_id = client.get('client_id')
        if not client_id:
            raise GmailOAuthError('Google OAuth credentials do not contain a client ID.')
        return client_id

    def _save_credentials(self, credentials, account: str | None = None) -> None:
        if not self.token_file:
            raise GmailOAuthError('GMAIL_TOKEN_FILE is not set.')
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        payload = json.loads(credentials.to_json())
        # credentials.to_json() drops id_token, so the verified identity is persisted here instead of re-derived on every load.
        payload['account'] = account if account is not None else payload.get('account', '')
        temporary = self.token_file.with_suffix(self.token_file.suffix + '.tmp')
        temporary.write_text(json.dumps(payload), encoding='utf-8')
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        temporary.replace(self.token_file)
        try:
            os.chmod(self.token_file, 0o600)
        except OSError:
            pass
        logger.info('Gmail OAuth token persisted; token_path=%s', self.token_file)

    def _load_credentials(self):
        credentials_file, token_file = self._require_paths()
        Request, Credentials, _, _ = self._load_google()
        credentials = None
        verified_account = ''
        if token_file.is_file():
            try:
                token_metadata = json.loads(token_file.read_text(encoding='utf-8'))
                if not _required_scopes_present(token_metadata.get('scopes')):
                    raise GmailOAuthError('Saved Gmail token is stale or incompatible. Reauthorize Gmail with gmail.send, openid, and email.')
                verified_account = str(token_metadata.get('account') or '')
                credentials = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            except GmailOAuthError:
                raise
            except (ValueError, json.JSONDecodeError) as exc:
                raise GmailOAuthError('The saved Gmail token is invalid. Use Reauthorize Gmail.') from exc
        if credentials and not _required_scopes_present(credentials.scopes):
            raise GmailOAuthError('Saved Gmail token is stale or incompatible. Reauthorize Gmail with gmail.send, openid, and email.')
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                self._save_credentials(credentials, verified_account)
            except Exception as exc:
                raise GmailOAuthError('Gmail token refresh failed. Use Reauthorize Gmail.') from exc
        if not credentials or not credentials.valid:
            raise GmailOAuthError('OAUTH_REQUIRED: authorize Gmail before sending.')
        credentials._letrusto_verified_account = verified_account
        return credentials

    def _authenticated_email(self, credentials) -> str:
        id_token_value = getattr(credentials, 'id_token', None)
        if not id_token_value:
            verified_account = getattr(credentials, '_letrusto_verified_account', '')
            if verified_account:
                return verified_account
            raise GmailOAuthError('OAuth token is missing OpenID identity information. Reauthorize Gmail.')
        try:
            Request, _, id_token, _ = self._load_google()
            claims = id_token.verify_oauth2_token(id_token_value, Request(), audience=self._client_id())
        except Exception as exc:
            logger.warning('Gmail OAuth identity verification failed; exception_type=%s message=%s', type(exc).__name__, str(exc)[:200])
            raise GmailOAuthError('Unable to verify the OpenID Gmail account.') from exc
        account = str(claims.get('email') or '').lower()
        if not account or claims.get('email_verified') is False:
            raise GmailOAuthError('OAuth identity did not provide a verified email address. Reauthorize Gmail.')
        logger.info('Gmail OAuth identity received; authenticated_email=%s expected_email=%s', account, EXPECTED_ACCOUNT)
        return account

    def verify_sender(self, credentials=None) -> str:
        account = self._authenticated_email(credentials or self._load_credentials())
        if account != EXPECTED_ACCOUNT:
            raise GmailOAuthError('Connected Gmail account is not hello@letrusto.com.')
        return account

    def status(self) -> dict:
        result = {'authorized': False, 'account': None, 'scope': _scope_string(SCOPES), 'token_valid': False, 'sender': EXPECTED_ACCOUNT, 'configured': bool(self.credentials_file and self.credentials_file.is_file()), 'message': '', 'token_path_warning': self._token_path_warning()}
        if not self.credentials_file:
            result['message'] = 'Set GMAIL_CREDENTIALS_FILE.'; return result
        if not self.token_file:
            result['message'] = 'Set GMAIL_TOKEN_FILE.'; return result
        if not self.credentials_file.is_file():
            result['message'] = 'Credentials file not found.'; return result
        if not self.token_file.is_file():
            result['message'] = 'Not connected. Click Connect Gmail.'; return result
        try:
            try:
                token_metadata = json.loads(self.token_file.read_text(encoding='utf-8'))
                result['scope'] = _scope_string(token_metadata.get('scopes'))
            except (OSError, ValueError, json.JSONDecodeError):
                pass
            credentials = self._load_credentials()
            try:
                result['scope'] = _scope_string(credentials.scopes)
                account = self._authenticated_email(credentials)
                result['account'] = account
                result['authorized'] = account == EXPECTED_ACCOUNT
                result['token_valid'] = result['authorized']
                result['message'] = '' if result['authorized'] else 'Connected Gmail account is not hello@letrusto.com.'
            except GmailOAuthError as exc:
                result['message'] = str(exc)
        except GmailOAuthError as exc:
            result['message'] = str(exc)
        return result

    def start_authorization(self) -> str:
        credentials_file, _ = self._require_paths()
        _, _, _, installed_flow = self._load_google()
        factory = self.flow_factory or installed_flow.from_client_secrets_file
        try:
            flow = factory(str(credentials_file), SCOPES)
            flow.redirect_uri = callback_uri_for_request(configured_uri=self.redirect_uri)
            state = secrets.token_urlsafe(32)
            with _flow_lock:
                _pending_flows[state] = flow
            authorization_url, _ = flow.authorization_url(access_type='offline', prompt='consent', include_granted_scopes='false', state=state, nonce=secrets.token_urlsafe(32))
            logger.info('Gmail OAuth authorization started; callback_path=%s', OAUTH_CALLBACK_PATH)
            return authorization_url
        except (ValueError, OSError) as exc:
            raise GmailOAuthError('Invalid Google OAuth credentials JSON.') from exc

    def finish_authorization(self, code: str, state: str | None) -> str:
        if not code or not state:
            raise GmailOAuthError('OAuth callback did not include a code and state.')
        with _flow_lock:
            flow = _pending_flows.pop(state, None)
        if not flow:
            raise GmailOAuthError('OAuth state expired or is invalid. Start Connect Gmail again.')
        try:
            previous_relax_scope = os.environ.get('OAUTHLIB_RELAX_TOKEN_SCOPE')
            os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
            try:
                flow.fetch_token(code=code)
            finally:
                if previous_relax_scope is None:
                    os.environ.pop('OAUTHLIB_RELAX_TOKEN_SCOPE', None)
                else:
                    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = previous_relax_scope
            credentials = flow.credentials
            if not credentials or not credentials.valid:
                raise GmailOAuthError('OAuth token is invalid. Reauthorize Gmail.')
            if not _required_scopes_present(credentials.scopes):
                raise GmailOAuthError('OAuth returned incompatible scopes. Reauthorize Gmail with gmail.send, openid, and email.')
            logger.info('Gmail OAuth token exchange succeeded; granted_scopes=%s', _scope_string(credentials.scopes))
            account = self.verify_sender(credentials)
            self._save_credentials(credentials, account)
            logger.info('Gmail OAuth verification succeeded; verification_result=accepted')
            return account
        except GmailOAuthError:
            raise
        except Exception as exc:
            logger.warning('Gmail OAuth token exchange failed; exception_type=%s message=%s', type(exc).__name__, str(exc)[:300])
            raise GmailOAuthError('Google authorization failed or was denied.') from exc

    def send(self, recipient: str, subject: str, body: str) -> str:
        credentials = self._load_credentials()
        self.verify_sender(credentials)
        try:
            from googleapiclient.discovery import build
            message = EmailMessage(); message['To'] = recipient; message['From'] = EXPECTED_ACCOUNT; message['Subject'] = subject; message.set_content(body)
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            result = build('gmail', 'v1', credentials=credentials, cache_discovery=False).users().messages().send(userId='me', body={'raw': raw}).execute()
            return result.get('id', '')
        except ImportError as exc:
            raise GmailOAuthError('Install google-api-python-client before sending.') from exc
