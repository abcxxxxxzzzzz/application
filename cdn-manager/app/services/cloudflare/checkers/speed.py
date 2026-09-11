from app.services.checker.base import (
    BaseChecker,
    CheckResult,
)
from app.services.checker.diff import build_diff


class SpeedChecker(BaseChecker):

    async def check(
        self,
        domain: str,
        config: dict,
        context: dict,
    ) -> CheckResult:

        expected = config

        actual = context.get(
            "speed",
            {},
        )

        diff = build_diff(
            expected,
            actual,
        )

        return CheckResult(
            rule_code="SPEED",
            status="PASS" if not diff else "FAIL",
            expected=expected,
            actual=actual,
            diff=diff,
        )