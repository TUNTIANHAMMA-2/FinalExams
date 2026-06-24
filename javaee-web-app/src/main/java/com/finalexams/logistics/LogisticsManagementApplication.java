package com.finalexams.logistics;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@MapperScan("com.finalexams.logistics.mapper")
@SpringBootApplication
/**
 * 项目启动入口。
 *
 * <p>{@code @MapperScan} 用于让 MyBatis-Plus 自动发现 mapper 包下的接口。</p>
 */
public class LogisticsManagementApplication {

    public static void main(String[] args) {
        SpringApplication.run(LogisticsManagementApplication.class, args);
    }
}
