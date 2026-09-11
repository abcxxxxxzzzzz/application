                         Group
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          Origin        CF Rule       Domains
       一个回源地址      一个规则         多个
                                         │
                       ┌─────────────────┼───────────────┐
                       │                 │               │
                       ▼                 ▼               ▼
                    Domain 1          Domain 2        Domain 3
                       │                 │               │
                    CF/AWS            CF/AWS          OTHER
                       │
                  CF DNS 实际状态
                       │
                ┌──────┴──────┐
                │             │
          proxied=true   proxied=false
                │             │
                ▼             ▼
               CF          CNAME 判断




                 ┌──────────────┐
                 │  cf_rules    │
                 └──────┬───────┘
                        │
                        │ 1:1
                        ▼
┌──────────────┐   ┌──────────────┐
│    groups    │──▶│ cf_rule_items│
└──────┬───────┘   └──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│   domains    │
└──────┬───────┘
       │
       │ N:1
       ▼
┌──────────────┐
│cdn_accounts  │
└──────────────┘


groups
  │
  │ 1:N
  ▼
tasks
  │
  │ 1:N
  ▼
task_items
  │
  │ N:1
  ▼
domains






                    ┌─────────────────┐
                    │    cdn_accounts │
                    └────────┬────────┘
                             │
                             │ 1:N
                             ▼
┌─────────────────┐     ┌─────────────────┐
│    cf_rules     │     │     domains     │
│                 │     │                 │
│ API_STANDARD    │     │ api01.xxx.com  │
│ H5_STANDARD     │     │ api02.xxx.com  │
│ SPECIAL         │     │ api03.xxx.com  │
└────────┬────────┘     └────────▲────────┘
         │                        │
         │ 1:N                    │ N:1
         ▼                        │
┌─────────────────┐               │
│     groups      │───────────────┘
│                 │
│ API             │
│ H5              │
│ SPECIAL         │
└────────┬────────┘
         │
         │ 1:N
         ▼
      domains


CFRule
  │
  └── CFRuleItem
        ├── NS
        ├── SSL
        ├── HSTS
        ├── SECURITY
        ├── RATE_LIMIT
        ├── SPEED
        ├── CACHE
        └── NETWORK


Group
  │
  └── Tasks
        │
        └── TaskItems
              │
              └── Domain