

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── config/             # 配置文件与配置解析
│   ├── config.go       # 配置结构体定义
│   └── config.yaml     # 环境配置文件
├── global/             # 全局变量 (如 DB、Redis、日志实例等)
│   └── global.go       
├── initialize/         # 初始化流程 (配置、数据库、日志、路由等)
│   ├── db.go           
│   ├── logger.go       
│   └── router.go       
├── internal/           # 核心业务逻辑 (内聚不外露)
│   ├── controller/     # 控制器层：解析参数、返回响应
│   ├── middleware/     # 中间件：JWT、跨域、日志拦截等
│   ├── model/          # 模型层：数据库结构体、请求/响应结构体
│   ├── repository/     # 持久层：数据库增删改查
│   └── service/        # 业务逻辑层：核心业务组合
├── pkg/                # 公共工具包 (可复用于其他项目)
│   ├── response/       # 统一响应封装
│   └── utils/          # 加密、时间等工具函数
├── main.go             # 项目启动入口
├── go.mod              
└── README.md      