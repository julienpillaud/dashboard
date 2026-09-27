from decimal import Decimal

from app.domain.pricing.entities import (
    PricingConfig,
    RoundConfig,
    ThresholdAdjustment,
)

PRICING_CONFIGS_MAP = {
    "ABSINTHE": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "ACCESSOIRE": PricingConfig(
        value=Decimal("1.06"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "ALIMENTATION": PricingConfig(
        value=Decimal("1.06"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "ANISÉ": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "ARMAGNAC": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "BIB": PricingConfig(
        value=Decimal("5"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=None,
    ),
    "BIÈRE": PricingConfig(
        value=Decimal("1.7"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "BSA": PricingConfig(
        value=Decimal("1.06"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "CACHAÇA": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "CIDRE": PricingConfig(
        value=Decimal("1.7"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "COFFRET": PricingConfig(
        value=Decimal("1.5"),
        operator="*",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=None,
    ),
    "COGNAC": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "EMBALLAGE": PricingConfig(
        value=Decimal("1.06"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "FÛT": PricingConfig(
        value=Decimal("32.5"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=None,
    ),
    "GIN": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "LIQUEUR": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "MADÈRE": PricingConfig(
        value=Decimal("1.5"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "MEZCAL": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "MINI-FÛT": PricingConfig(
        value=Decimal("5"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=None,
    ),
    "PINEAU": PricingConfig(
        value=Decimal("1.5"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "PORTO": PricingConfig(
        value=Decimal("1.5"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "RHUM": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "RHUM ARRANGÉ": PricingConfig(
        value=Decimal("5"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=None,
    ),
    "VIN": PricingConfig(
        value=Decimal("1.5"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "VIN EFFERVESCENT": PricingConfig(
        value=Decimal("1.5"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "VIN MUTÉ": PricingConfig(
        value=Decimal("1.5"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
    "VODKA": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "WHISKY": PricingConfig(
        value=Decimal("10"),
        operator="+",
        round_config=RoundConfig(value=Decimal("1"), round_mode="ROUND_HALF_EVEN"),
        adjustment=ThresholdAdjustment(
            threshold=Decimal("100"), extra_value=Decimal("10")
        ),
    ),
    "XÉRÈS": PricingConfig(
        value=Decimal("1.5"),
        operator="*",
        round_config=RoundConfig(value=Decimal("0.05"), round_mode="ROUND_CEILING"),
        adjustment=None,
    ),
}
