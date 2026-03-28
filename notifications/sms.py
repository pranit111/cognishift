"""
SMS integration for CogniShift via kutility.org API.

API Response format:
  Success: SMS-SHOOT-ID/{alpha-numeric}
  Error:   ERR: {MESSAGE}
"""
import logging
from typing import Tuple

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:
    """SMS Service using Kutility API."""

    def __init__(self):
        self.api_url = settings.SMS_API_URL
        self.api_key = settings.SMS_API_KEY
        self.campaign = settings.SMS_CAMPAIGN
        self.route_id = settings.SMS_ROUTE_ID
        self.sender_id = settings.SMS_SENDER_ID
        self.template_id = settings.SMS_TEMPLATE_ID
        self.pe_id = settings.SMS_PE_ID
        self.enabled = settings.SMS_ENABLED

    def _call(self, phone: str, message: str) -> Tuple[bool, str]:
        """Internal: make the API request and parse the response."""
        params = {
            'key': self.api_key,
            'campaign': self.campaign,
            'routeid': self.route_id,
            'type': 'text',
            'contacts': phone,
            'senderid': self.sender_id,
            'msg': message,
            'template_id': self.template_id,
            'pe_id': self.pe_id,
        }
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            text = response.text.strip()
            logger.info("SMS API response for %s: %s", phone, text)

            if text.startswith('ERR:'):
                error = text[4:].strip()
                logger.error("SMS API error: %s", error)
                return False, error
            if text.startswith('SMS-SHOOT-ID/'):
                shoot_id = text.split('/')[1]
                logger.info("SMS sent. Shoot ID: %s", shoot_id)
                return True, shoot_id
            logger.warning("Unexpected SMS API response: %s", text)
            return False, f"Unexpected response: {text}"
        except requests.RequestException as e:
            logger.error("SMS connection error: %s", e)
            return False, f"Connection error: {e}"
        except Exception as e:
            logger.error("SMS error: %s", e)
            return False, f"Error: {e}"

    def send_otp(self, phone: str, otp: str) -> Tuple[bool, str]:
        """
        Send an OTP verification SMS.

        Args:
            phone: 10-digit phone number
            otp:   6-digit OTP code

        Returns:
            (success, shoot_id_or_error_message)
        """
        if not self.enabled:
            logger.warning("SMS disabled. OTP for %s: %s", phone, otp)
            return True, f"SMS_DISABLED_OTP_{otp}"

        message = (
            f"This is your CogniShift OTP, {otp}  "
          
        )
        logger.info("Sending OTP SMS to %s", phone)
        return self._call(phone, message)

    def send_notification(self, phone: str, source_app: str, message: str, priority: str) -> Tuple[bool, str]:
        """
        Send a CogniShift notification alert via SMS.

        Args:
            phone:      10-digit phone number
            source_app: e.g. 'github', 'slack'
            message:    notification body
            priority:   'low' | 'medium' | 'high'

        Returns:
            (success, shoot_id_or_error_message)
        """
        if not self.enabled:
            logger.warning("SMS disabled. Notification for %s skipped.", phone)
            return True, "SMS_DISABLED"

        sms_text = f"[CogniShift | {priority.upper()}] {source_app}: {message}"
        logger.info("Sending notification SMS to %s (priority=%s)", phone, priority)
        return self._call(phone, sms_text)

    def send_custom_sms(self, phone: str, message: str) -> Tuple[bool, str]:
        """
        Send a custom SMS (welcome messages, queue-drained alerts, etc.)

        Returns:
            (success, shoot_id_or_error_message)
        """
        if not self.enabled:
            logger.warning("SMS disabled. Custom message for %s skipped.", phone)
            return True, "SMS_DISABLED"

        logger.info("Sending custom SMS to %s", phone)
        return self._call(phone, message)


# Singleton — import and use directly: from .sms import sms_service
sms_service = SMSService()
