from app.services.checker.base import (
    BaseChecker,
    CheckResult,
)
from app.services.checker.diff import build_diff


class NetworkChecker(BaseChecker):

    async def check(
        self,
        domain: str,
        config: dict,
        context: dict,
    ) -> CheckResult:

        expected = {
            "ipv6": config.get(
                "ipv6",
                False,
            ),
            "ipv4_over_ipv6": config.get(
                "ipv4_over_ipv6",
                True,
            ),
        }

        actual = context.get(
            "network",
            {},
        )

        diff = build_diff(
            expected,
            actual,
        )

        return CheckResult(
            rule_code="NETWORK",
            status="PASS" if not diff else "FAIL",
            expected=expected,
            actual=actual,
            diff=diff,
        )