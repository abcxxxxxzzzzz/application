from app.services.checker.base import (
    BaseChecker,
    CheckResult,
)
from app.services.checker.diff import build_diff


class SecurityChecker(BaseChecker):

    async def check(
        self,
        domain: str,
        config: dict,
        context: dict,
    ) -> CheckResult:

        expected = {
            "ip_whitelist": sorted(
                config.get(
                    "ip_whitelist",
                    [],
                )
            ),
            "geo_allow": sorted(
                config.get(
                    "geo_allow",
                    [],
                )
            ),
            "geo_deny": sorted(
                config.get(
                    "geo_deny",
                    [],
                )
            ),
            "custom_rules": config.get(
                "custom_rules",
                [],
            ),
        }

        actual = context.get(
            "security",
            {},
        )

        diff = build_diff(
            expected,
            actual,
        )

        return CheckResult(
            rule_code="SECURITY",
            status="PASS" if not diff else "FAIL",
            expected=expected,
            actual=actual,
            diff=diff,
        )