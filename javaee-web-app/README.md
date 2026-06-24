# 物流管理系统（JavaEE 课程设计）

这是一个用于期末课程设计提交和答辩演示的 Spring Boot 物流管理系统。项目保留常见 JavaEE 作业需要展示的核心内容：Spring MVC 页面、RESTful 接口、MyBatis-Plus 持久层、MySQL 建表脚本、统一响应封装和事务控制。

旧版 RhizoDelta 报告资料已归档到：`../archived-projects/javaee-web-app-rhizodelta-report-2026-06-24/`。

## 技术栈

- Java 17
- Spring Boot 3.2.3
- Spring MVC
- Thymeleaf
- MyBatis-Plus
- MySQL
- Lombok
- Bean Validation
- Spring Boot DevTools

## 功能模块

- 工作台：首页展示客户、司机、车辆、运单数量和运单状态统计。
- 基础资料：展示客户、司机、车辆测试数据。
- 运单管理：支持查询、新增、编辑、删除物流运单。
- REST 接口：提供 `/api/shipments` 的 GET、POST、PUT、DELETE 接口。
- 统一响应：REST 接口统一返回 `code`、`message`、`data` 字段。
- 事务控制：运单新增、修改、删除方法使用 `@Transactional`。

## 运行步骤

### 推荐方式：Docker 启动 MySQL

这种方式不需要系统安装 `mysql` 命令行客户端。MySQL 容器第一次启动时会自动执行 `sql/schema.sql` 和 `sql/data.sql`。

1. 启动项目专用 MySQL：

   ```bash
   docker compose up -d mysql
   ```

2. 确认 MySQL 容器运行正常：

   ```bash
   docker compose ps
   ```

3. 启动 Spring Boot 项目：

   ```bash
   mvn spring-boot:run
   ```

4. 浏览器访问：

   ```text
   http://localhost:18090
   ```

默认连接信息已经与 `application-dev.yml` 对齐：数据库 `logistics_db`，账号 `root`，密码 `root`，端口 `3306`。

如果本机 3306 端口已被占用，可以把 `docker-compose.yml` 里的 `3306:3306` 改成例如 `3307:3306`，同时把 `application-dev.yml` 的 JDBC 地址改成 `localhost:3307`。

### 备选方式：本机 MySQL 手动导入

如果本机已经安装 MySQL 服务和 `mysql` 命令行客户端，也可以手动导入 SQL。

1. 创建数据库并导入表结构：

   ```bash
   mysql -uroot -p < sql/schema.sql
   ```

2. 导入测试数据：

   ```bash
   mysql -uroot -p < sql/data.sql
   ```

3. 按本机 MySQL 账号修改 `src/main/resources/application-dev.yml`：

   ```yaml
   spring:
     datasource:
       username: root
       password: root
   ```

4. 启动项目：

   ```bash
   mvn spring-boot:run
   ```

5. 浏览器访问：

   ```text
   http://localhost:18090
   ```

## REST 接口示例

查询运单：

```bash
curl "http://localhost:18090/api/shipments?status=CREATED"
```

新增运单：

```bash
curl -X POST "http://localhost:18090/api/shipments" \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": 1,
    "driverId": 1,
    "vehicleId": 1,
    "originAddress": "广州白云仓",
    "destinationAddress": "深圳南山科技园",
    "cargoName": "电子配件",
    "cargoWeight": 2.5,
    "freightFee": 1500,
    "status": "CREATED",
    "remark": "接口测试新增"
  }'
```

修改运单：

```bash
curl -X PUT "http://localhost:18090/api/shipments/1" \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": 1,
    "driverId": 2,
    "vehicleId": 2,
    "originAddress": "广州白云仓",
    "destinationAddress": "深圳南山科技园",
    "cargoName": "电子配件",
    "cargoWeight": 3.0,
    "freightFee": 1800,
    "status": "IN_TRANSIT",
    "remark": "已安排运输"
  }'
```

删除运单：

```bash
curl -X DELETE "http://localhost:18090/api/shipments/1"
```

## 项目结构

```text
src/main/java/com/finalexams/logistics
├── common        # 统一响应和异常处理
├── controller    # 页面 Controller 和 REST Controller
├── entity        # MyBatis-Plus 实体类
├── mapper        # Mapper 接口
└── service       # 业务服务和事务控制

src/main/resources
├── application.yml
├── application-dev.yml
├── application-prod.yml
├── static/css/app.css
└── templates     # Thymeleaf 页面

sql
├── schema.sql    # 建表脚本
└── data.sql      # 测试数据
```

## 答辩演示建议

1. 展示 `application-dev.yml`，说明端口、数据源和 MyBatis-Plus SQL 日志配置。
2. 展示 `sql/schema.sql`，说明客户、司机、车辆、运单四张表。
3. 展示 `ShipmentRestController`，说明 RESTful 接口和参数接收方式。
4. 展示 `ApiResponse`，说明统一响应结构。
5. 展示 `ShipmentServiceImpl`，说明 `@Transactional` 事务控制。
6. 启动项目，演示首页统计、运单查询、新增、编辑、删除。
