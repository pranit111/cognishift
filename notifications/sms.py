"""
SMS integration for CogniShift.

Two providers:
  - Kutility (kutility.org)  → OTP / verification SMS
  - Fast2SMS (fast2sms.com)  → High-priority notification alerts

API Response formats:
  Kutility  success: SMS-SHOOT-ID/{alpha-numeric}
  Kutility  error:   ERR: {MESSAGE}
  Fast2SMS  success: { "return": true, "request_id": "...", ... }
  Fast2SMS  error:   { "return": false, "message": [...] }
"""
import logging
from typing import Tuple

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:
    """SMS Service — Kutility for OTP, Fast2SMS for notification alerts."""

    def __init__(self):
        # Kutility settings (OTP)
        self.kutility_url = settings.SMS_API_URL
        self.kutility_key = settings.SMS_API_KEY
        self.kutility_campaign = settings.SMS_CAMPAIGN
        self.kutility_route = settings.SMS_ROUTE_ID
        self.kutility_sender = settings.SMS_SENDER_ID
        self.kutility_template_id = settings.SMS_TEMPLATE_ID
        self.kutility_pe_id = settings.SMS_PE_ID

        # Fast2SMS settings (notifications)
        self.fast2sms_url = settings.FAST2SMS_API_URL
        self.fast2sms_key = settings.FAST2SMS_API_KEY

        self.enabled = settings.SMS_ENABLED

    # ------------------------------------------------------------------ #
    #  Kutility — OTP                                                      #
    # ------------------------------------------------------------------ #

    def _kutility_call(self, phone: str, message: str) -> Tuple[bool, str]:
        """Make a Kutility API request and parse the response."""
        params = {
            'key': self.kutility_key,
            'campaign': self.kutility_campaign,
            'routeid': self.kutility_route,
            'type': 'text',
            'contacts': phone,
            'senderid': self.kutility_sender,
            'msg': message,
            'template_id': self.kutility_template_id,
            'pe_id': self.kutility_pe_id,
        }
        try:
            response = requests.get(self.kutility_url, params=params, timeout=10)
            text = response.text.strip()
            logger.info("Kutility SMS response for %s: %s", phone, text)

            if text.startswith('ERR:'):
                error = text[4:].strip()
                logger.error("Kutility SMS error: %s", error)
                return False, error
            if text.startswith('SMS-SHOOT-ID/'):
                shoot_id = text.split('/')[1]
                logger.info("Kutility SMS sent. Shoot ID: %s", shoot_id)
                return True, shoot_id
            logger.warning("Unexpected Kutility response: %s", text)
            return False, f"Unexpected response: {text}"
        except requests.RequestException as e:
            logger.error("Kutility connection error: %s", e)
            return False, f"Connection error: {e}"
        except Exception as e:
            logger.error("Kutility error: %s", e)
            return False, f"Error: {e}"

    def send_otp(self, phone: str, otp: str) -> Tuple[bool, str]:
        """
        Send OTP via Kutility.

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
            f"Dear Customer, {otp} this is your mobile verification OTP. "
            f"Please do not share with anyone. Best Regards, "
            f"https://www.masterkeypro.in DARSHAN KATARIYA"
        )
        logger.info("Sending OTP via Kutility to %s", phone)
        return self._kutility_call(phone, message)

    # ------------------------------------------------------------------ #
    #  Fast2SMS — notification alerts                                      #
    # ------------------------------------------------------------------ #

    def _fast2sms_call(self, phone: str, message: str) -> Tuple[bool, str]:
        """Make a Fast2SMS API request and parse the response."""
        params = {
            'authorization': self.fast2sms_key,
            'message': message,
            'route': 'q',
            'numbers': phone,
            'flash': '0',
        }
        headers = {'accept': 'application/json'}
        try:
            response = requests.get(self.fast2sms_url, params=params, headers=headers, timeout=10)
            data = response.json()
            logger.info("Fast2SMS response for %s: %s", phone, data)

            if data.get('return'):
                request_id = data.get('request_id', '')
                logger.info("Fast2SMS sent. Request ID: %s", request_id)
                return True, request_id
            error = str(data.get('message', 'Unknown error'))
            logger.error("Fast2SMS error: %s", error)
            return False, error
        except requests.RequestException as e:
            logger.error("Fast2SMS connection error: %s", e)
            return False, f"Connection error: {e}"
        except Exception as e:
            logger.error("Fast2SMS error: %s", e)
            return False, f"Error: {e}"

    def send_notification(self, phone: str, source_app: str, message: str, priority: str) -> Tuple[bool, str]:
        """
        Send a high-priority notification alert via Fast2SMS.

        Args:
            phone:      10-digit phone number
            source_app: e.g. 'github', 'slack'
            message:    notification body
            priority:   'low' | 'medium' | 'high'

        Returns:
            (success, request_id_or_error_message)
        """
        if not self.enabled:
            logger.warning("SMS disabled. Notification for %s skipped.", phone)
            return True, "SMS_DISABLED"

        sms_text = f"[CogniShift | {priority.upper()}] {source_app}: {message}"
        logger.info("Sending notification via Fast2SMS to %s (priority=%s)", phone, priority)
        return self._fast2sms_call(phone, sms_text)

    def send_custom_sms(self, phone: str, message: str) -> Tuple[bool, str]:
        """
        Send a custom SMS via Fast2SMS (queue-drained alerts, welcome messages, etc.)

        Returns:
            (success, request_id_or_error_message)
        """
        if not self.enabled:
            logger.warning("SMS disabled. Custom message for %s skipped.", phone)
            return True, "SMS_DISABLED"

        logger.info("Sending custom SMS via Fast2SMS to %s", phone)
        return self._fast2sms_call(phone, message)


# Singleton — import and use: from .sms import sms_service
sms_service = SMSService()
