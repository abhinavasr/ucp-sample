"""
Merchant Payment Agent - Ollama-based AP2 payment processor
Integrated within merchant backend, uses same Ollama instance as chat backend.
"""

import uuid
import random
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from ap2_types import (
    PaymentMandate,
    PaymentReceipt,
    PaymentReceiptSuccess,
    PaymentReceiptError,
    PaymentReceiptFailure,
    PaymentCurrencyAmount,
    OTPChallenge
)

logger = logging.getLogger(__name__)


class MerchantPaymentAgent:
    """
    Merchant-side payment agent for AP2 protocol.
    Receives signed payment mandates from consumer and processes payments.
    """

    def __init__(self, ollama_url: Optional[str] = None, model_name: str = "qwen2.5:8b"):
        """
        Initialize merchant payment agent.

        Args:
            ollama_url: URL of Ollama server (optional, can use same as chat backend)
            model_name: Ollama model to use for payment processing logic
        """
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.pending_otps: Dict[str, str] = {}  # mandate_id -> otp

        logger.info(f"Merchant Payment Agent initialized (model: {model_name})")

    def validate_mandate_signature(self, mandate: PaymentMandate) -> bool:
        """
        Validate payment mandate signature.
        In production, this would verify the WebAuthn signature.
        For demo, we check if signature exists.
        """
        if not mandate.user_authorization:
            logger.warning(f"Mandate {mandate.payment_mandate_contents.payment_mandate_id} missing signature")
            return False

        # In production: verify signature using public key from consumer
        # For demo: accept if signature exists and is non-empty
        if len(mandate.user_authorization) < 10:
            logger.warning(f"Mandate {mandate.payment_mandate_contents.payment_mandate_id} has invalid signature")
            return False

        logger.info(f"Mandate {mandate.payment_mandate_contents.payment_mandate_id} signature validated")
        return True

    def should_raise_otp_challenge(self, mandate: PaymentMandate) -> bool:
        """
        Determine if OTP challenge should be raised.
        In production: based on risk scoring, transaction amount, user history.
        For demo: random 10% chance.
        """
        # Simple rules:
        # 1. Amounts over $100: 30% chance
        # 2. Amounts under $100: 10% chance

        amount = mandate.payment_mandate_contents.payment_details_total.amount.value

        if amount > 100:
            challenge_probability = 0.3
        else:
            challenge_probability = 0.1

        should_challenge = random.random() < challenge_probability

        if should_challenge:
            logger.info(f"OTP challenge triggered for mandate {mandate.payment_mandate_contents.payment_mandate_id}")

        return should_challenge

    def generate_otp(self, mandate_id: str) -> str:
        """Generate OTP for payment verification."""
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.pending_otps[mandate_id] = otp
        logger.info(f"Generated OTP for mandate {mandate_id}: {otp}")
        return otp

    def verify_otp(self, mandate_id: str, otp_code: str) -> bool:
        """Verify OTP code."""
        expected_otp = self.pending_otps.get(mandate_id)

        if not expected_otp:
            logger.warning(f"No OTP found for mandate {mandate_id}")
            return False

        if otp_code == expected_otp:
            # Remove OTP after successful verification
            del self.pending_otps[mandate_id]
            logger.info(f"OTP verified successfully for mandate {mandate_id}")
            return True

        logger.warning(f"Invalid OTP for mandate {mandate_id}")
        return False

    def process_payment(self, mandate: PaymentMandate) -> PaymentReceipt:
        """
        Process payment mandate and return receipt.

        This is the main AP2 payment processing flow:
        1. Validate mandate signature
        2. Process payment (simulate)
        3. Return receipt
        """
        mandate_id = mandate.payment_mandate_contents.payment_mandate_id

        # Validate signature
        if not self.validate_mandate_signature(mandate):
            return PaymentReceipt(
                payment_mandate_id=mandate_id,
                timestamp=datetime.utcnow().isoformat(),
                payment_id=f"ERR-{uuid.uuid4().hex[:8]}",
                amount=mandate.payment_mandate_contents.payment_details_total.amount,
                payment_status=PaymentReceiptError(
                    error_message="Invalid mandate signature"
                )
            )

        # Simulate payment processing
        # In production: call actual payment gateway
        payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        merchant_confirmation = f"MCH-{uuid.uuid4().hex[:8].upper()}"
        psp_confirmation = f"PSP-{uuid.uuid4().hex[:8].upper()}"
        network_confirmation = f"NET-{uuid.uuid4().hex[:8].upper()}"

        logger.info(f"Processing payment for mandate {mandate_id}: {payment_id}")

        # Simulate success (95% success rate)
        if random.random() < 0.95:
            receipt = PaymentReceipt(
                payment_mandate_id=mandate_id,
                timestamp=datetime.utcnow().isoformat(),
                payment_id=payment_id,
                amount=mandate.payment_mandate_contents.payment_details_total.amount,
                payment_status=PaymentReceiptSuccess(
                    merchant_confirmation_id=merchant_confirmation,
                    psp_confirmation_id=psp_confirmation,
                    network_confirmation_id=network_confirmation
                ),
                payment_method_details={
                    "method": mandate.payment_mandate_contents.payment_response.method_name,
                    "payer_email": mandate.payment_mandate_contents.payment_response.payer_email
                }
            )
            logger.info(f"Payment successful: {payment_id}")
        else:
            # Simulate failure
            receipt = PaymentReceipt(
                payment_mandate_id=mandate_id,
                timestamp=datetime.utcnow().isoformat(),
                payment_id=payment_id,
                amount=mandate.payment_mandate_contents.payment_details_total.amount,
                payment_status=PaymentReceiptFailure(
                    failure_message="Payment declined by issuing bank"
                )
            )
            logger.warning(f"Payment failed: {payment_id}")

        return receipt

    def create_otp_challenge(self, mandate: PaymentMandate) -> OTPChallenge:
        """Create OTP challenge for mandate."""
        mandate_id = mandate.payment_mandate_contents.payment_mandate_id
        otp = self.generate_otp(mandate_id)

        # In production: send OTP via SMS/email
        # For demo: just log it
        payer_email = mandate.payment_mandate_contents.payment_response.payer_email

        return OTPChallenge(
            payment_mandate_id=mandate_id,
            message=f"OTP verification required. Code sent to {payer_email}",
            otp_sent_to=payer_email
        )
