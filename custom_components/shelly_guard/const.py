"""Constants for the Shelly Guard integration."""

DOMAIN = "shelly_guard"
VERSION = "1.1.0"

CONF_BACKUP_DIR = "backup_dir"
CONF_KEEP_VERSIONS = "keep_versions"
CONF_AUTO_RESTORE = "auto_restore"
CONF_HARDEN = "harden"
CONF_NOTIFY_SERVICE = "notify_service"
CONF_NOTIFY_THREAD_ID = "notify_thread_id"
CONF_SHELLY_USER = "shelly_user"
CONF_SHELLY_PASSWORD = "shelly_password"
CONF_WIFI_PASSWORD = "wifi_password"
CONF_WIFI_SECRETS_FILE = "wifi_secrets_file"
CONF_NETALERTX_URL = "netalertx_url"
CONF_NETALERTX_TOKEN = "netalertx_token"
CONF_CHECK_INTERVAL_MIN = "check_interval_min"
CONF_SCAN_EVERY_MIN = "scan_every_min"
CONF_SCAN_DEVICES = "scan_devices"
CONF_SHOW_SIDEBAR = "show_sidebar"

DEFAULT_BACKUP_DIR = "/share/shelly_guard"
DEFAULT_KEEP_VERSIONS = 15
DEFAULT_AUTO_RESTORE = True
DEFAULT_HARDEN = True
DEFAULT_SHELLY_USER = "admin"
DEFAULT_WIFI_SECRETS_FILE = "/config/esphome/secrets.yaml"
DEFAULT_CHECK_INTERVAL_MIN = 60
DEFAULT_SCAN_EVERY_MIN = 60
DEFAULT_SCAN_DEVICES = 8
DEFAULT_SHOW_SIDEBAR = True
DEFAULT_WARRANTY_MONTHS = 36

MARKER_KEY = "shelly_guard"
HTTP_TIMEOUT = 8

STATIC_URL_PATH = "/shelly_guard_static"
PANEL_URL_PATH = "shelly-guard"
API_STATE_PATH = "/api/shelly_guard/state"

SIGNAL_UPDATE = f"{DOMAIN}_update"
