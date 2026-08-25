import requests

API = "http://127.0.0.1:8000/api/admin/domains/batch-create"

GROUP_ID = 1
TOTAL = 200_000
BATCH_SIZE = 1_000

domains = [
    f"test{i:06d}.test.com"
    for i in range(1, TOTAL + 1)
]

for start in range(0, TOTAL, BATCH_SIZE):

    batch = domains[
        start:start + BATCH_SIZE
    ]

    batch_no = start // BATCH_SIZE + 1

    target = (
        f"https://target{batch_no:03d}.test.com"
    )

    data = {
        "domains": batch,
        "group_id": GROUP_ID,
        "jump_type": "direct",
        "jump_method": "redirect",
        "status_code": 302,
        "target_domain": target,
        "embedded_code": None,
        "enabled": True,
        "pool": [],
    }

    print(
        f"[{batch_no}/100] "
        f"{len(batch)} domains -> {target}"
    )

    response = requests.post(
        API,
        json=data,
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()

    print(
        f"  created={result['created']} "
        f"skipped={result['skipped']}"
    )

print("完成")