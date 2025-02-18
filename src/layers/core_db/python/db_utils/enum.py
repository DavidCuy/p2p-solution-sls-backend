# -*- coding: utf-8 -*-
from enum import Enum

__all__ = [
    "StatusLoanEnum",
    "OfferStatusEnum",
    "OtpStatusEnum"
]


class StatusLoanEnum(Enum):
    ACTIVE = "ACTIVE"
    IN_PROCESS = "IN_PROCESS"
    CLOSED = "CLOSED"
    LATE = "LATE"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"


class OfferStatusEnum(Enum):
    NEW_OFFER = "S"
    OFFER_MODIFIED = "M"
    OFFER_REMOVED = "U"


class OtpStatusEnum(Enum):
    GENERATED = 1
    VALIDATED = 2
    EXPIRED = 3
