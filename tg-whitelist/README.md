export TG_TOKEN="你的TOKEN"
python bot.py





TG 白名单管理
/delete 666


##  Tip:

创建商户号: /create 666
绑定商户域: /bind 666 a.com
取消商户域: /unbind 666 a.com
商户后台添加白名单IP: /allow 666 1.1.1.1
商户后台删除白名单IP: /deny 666 1.1.1.1
查看商户号: /show 666
商户列表: /list





| 请求                     | 结果 |
| ---------------------- | -- |
| xfv10.com，无 Mid，IP正确   | 允许 |
| xfv10.com，Mid=666，IP正确 | 允许 |
| xfv10.com，Mid=777，IP正确 | 拒绝 |
| xfv10.com，无 Mid，IP错误   | 拒绝 |
| abc.com，没有MID绑定        | 拒绝 |
