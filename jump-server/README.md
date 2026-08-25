POST   /api/admin/groups
GET    /api/admin/groups
GET    /api/admin/groups/{id}
PUT    /api/admin/groups/{id}
DELETE /api/admin/groups/{id}

POST   /api/admin/domains
GET    /api/admin/domains
GET    /api/admin/domains/{id}
PUT    /api/admin/domains/{id}
DELETE /api/admin/domains/{id}

POST   /api/admin/domains/{id}/pool
GET    /api/admin/domains/{id}/pool
PUT    /api/admin/domains/{id}/pool/{pool_id}
DELETE /api/admin/domains/{id}/pool/{pool_id}


## 测试直接跳转

curl -X POST \
  http://127.0.0.1:8000/api/admin/groups \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "测试组"
  }'


curl -X POST \
  http://127.0.0.1:8000/api/admin/domains \
  -H 'Content-Type: application/json' \
  -d '{
    "domain": "test.example.com",
    "group_id": 1,
    "jump_type": "direct",
    "jump_method": "redirect",
    "status_code": 302,
    "target_domain": "https://www.baidu.com"
  }'


curl -I \
  -H 'Host: test.example.com' \
  http://127.0.0.1:8000/






## 创建随机跳转

curl -X POST \
  http://127.0.0.1:8000/api/admin/domains \
  -H 'Content-Type: application/json' \
  -d '{
    "domain": "random.example.com",
    "group_id": 1,
    "jump_type": "random",
    "jump_method": "js",
    "status_code": 400,
    "default_target": "https://example.com",
    "pool": [
      {
        "target_domain": "https://a.example.com",
        "weight": 1
      },
      {
        "target_domain": "https://b.example.com",
        "weight": 3
      },
      {
        "target_domain": "https://c.example.com",
        "weight": 1
      }
    ]
  }'













  curl -X POST http://127.0.0.1:8000/api/admin/domains \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "1.com",
    "group_id": 1,
    "jump_type": "direct",
    "jump_method": "redirect",
    "status_code": 302,
    "target_domain": "https://1.example.com/a/b/c?a=1",
    "enabled": true
  }'

 curl -X POST http://127.0.0.1:8000/api/admin/domains \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "2.com",
    "group_id": 1,
    "jump_type": "wildcard",
    "jump_method": "js",
    "status_code": 400,
    "target_domain": "https://*.example.com/a/b/c?a=1",
    "enabled": true
  }'


curl -X POST http://127.0.0.1:8000/api/admin/domains \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "2.com",
    "group_id": 1,
    "jump_type": "random",
    "jump_method": "html",
    "status_code": 400,
    "target_domain": "https://*.example.com/a/b/c?a=1",
    "enabled": true
  }'




   curl -X POST http://127.0.0.1:8000/api/admin/domains \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "3.com",
    "group_id": 1,
    "jump_type": "random",
    "jump_method": "js",
    "status_code": 400,
    "enabled": true,
    "pool": [
      {
        "target_domain": "https://a.example.com",
        "weight": 1,
        "enabled": true
      },
      {
        "target_domain": "https://b.example.com",
        "weight": 1,
        "enabled": true
      },
      {
        "target_domain": "https://c.example.com",
        "weight": 1,
        "enabled": true
      },
      {
        "target_domain": "https://d.example.com",
        "weight": 1,
        "enabled": true
      }
    ]
  }'





curl -X POST http://127.0.0.1:8000/api/admin/domains \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "4.com",
    "group_id": 1,
    "jump_type": "random",
    "jump_method": "redirect",
    "status_code": 308,
    "enabled": true,
    "pool": [
      {
        "target_domain": "https://4a.example.com",
        "weight": 1,
        "enabled": true
      },
      {
        "target_domain": "https://4b.example.com",
        "weight": 1,
        "enabled": true
      },
      {
        "target_domain": "https://4c.example.com",
        "weight": 1,
        "enabled": true
      },
      {
        "target_domain": "https://4d.example.com",
        "weight": 1,
        "enabled": true
      }
    ]
  }'



                      请求
                      │
                      ▼
                 abc.com
                      │
                      ▼
             Redis 查 abc.com
                 │         │
               命中       未命中
                 │         │
                 │         ▼
                 │       MySQL
                 │         │
                 └────┬────┘
                      │
                      ▼
                 Domain 配置
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       direct      wildcard     random
          │           │           │
          ▼           ▼           ▼
       固定URL     随机生成      随机池
                      │
                      ▼
              https://*.xxx.com
                      │
                      ▼
                随机子域名
                      │
                      ▼
             最终跳转 URL
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       redirect       js         html


