from app.services.checker.base import (
    BaseChecker,
    CheckResult,
)
from app.services.checker.diff import build_diff


class HSTSChecker(BaseChecker):

    async def check(
        self,
        domain: str,
        config: dict,
        context: dict,
    ) -> CheckResult:

        expected = {
            "enabled": config.get(
                "enabled",
                True,
            ),
            "max_age": config.get(
                "max_age",
                31536000,
            ),
            "include_subdomains": config.get(
                "include_subdomains",
                True,
            ),
            "preload": config.get(
                "preload",
                False,
            ),
        }

        actual = context.get(
            "hsts",
            {},
        )

        diff = build_diff(
            expected,
            actual,
        )

        return CheckResult(
            rule_code="HSTS",
            status="PASS" if not diff else "FAIL",
            expected=expected,
            actual=actual,
            diff=diff,
        )