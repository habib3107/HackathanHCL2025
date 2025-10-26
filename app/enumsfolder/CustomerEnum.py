
import enum
class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class MaritalStatusEnum(str, enum.Enum):
    Single = "Single"
    Married = "Married"
    Divorced = "Divorced"
    Widowed = "Widowed"


class KYCStatusEnum(str, enum.Enum):
    Pending = "Pending"
    Verified = "Verified"
    Rejected = "Rejected"


class AccountTypeEnum(str, enum.Enum):
    Savings = "Savings"
    Current = "Current"
    FixedDeposit = "FixedDeposit"
    LoanAccount = "LoanAccount"


class CustomerStatusEnum(str, enum.Enum):
    Active = "Active"
    Inactive = "Inactive"
    Suspended = "Suspended"
    Closed = "Closed"


class RiskCategoryEnum(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
