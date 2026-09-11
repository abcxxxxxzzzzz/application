from app.services.checker.base import (
    BaseChecker,
    CheckResult,
)
from app.services.checker.diff import build_diff



class RateLimitChecker(BaseChecker):

    async def check(
        self,
        domain: str,
        config: dict,
        context: dict,
    ) -> CheckResult:

        expected = {
            "enabled": config.get(
                "enabled",
                False,
            ),
            "requests": config.get(
                "requests",
                100,
            ),
            "period": config.get(
                "period",
                60,
            ),
        }

        actual = context.get(
            "rate_limit",
            {},
        )

        diff = build_diff(
            expected,
            actual,
        )

        return CheckResult(
            rule_code="RATE_LIMIT",
            status="PASS" if not diff else "FAIL",
            expected=expected,
            actual=actual,
            diff=diff,
        )