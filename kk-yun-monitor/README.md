# KK Monitor

轻量级域名监控服务。

## 功能

- 多项目监控
- 一个项目对应一个域名
- 定时检测 KK API
- 自动解析返回结果
- 统计解析失败
- 统计访问失败
- Telegram 告警
- Docker 常驻运行

## 目录

kk-monitor/

├── monitor.py
├── config.py
├── telegram.py
├── config.yaml
├── requirements.txt
├── Dockerfile
└── docker-compose.yml

## 启动

构建镜像:

docker build -t kk-monitor .

启动:

docker compose up -d

查看日志:

docker logs -f kk-monitor

或者:

tail -f logs/monitor.log

## 配置

修改 config.yaml:

projects:
  - name: "项目名称"
    domain: "监控域名"

telegram_enable:
  是否开启 TG 通知

alarm_threshold:
  触发告警次数

alarm_cooldown:
  告警冷却时间

## 告警示例

🚨 KK Monitor Alarm

项目: kk-api
域名: www.kk.yun

时间:
2026-07-31 22:30:00

解析失败:
6

访问失败:
2

失败详情:
failed ip:1.1.1.1
failed ip:2.2.2.2