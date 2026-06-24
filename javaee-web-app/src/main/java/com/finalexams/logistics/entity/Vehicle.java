package com.finalexams.logistics.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("lm_vehicle")
/**
 * 车辆实体，对应数据库 lm_vehicle 表，记录车牌、车型和载重等信息。
 */
public class Vehicle {

    @TableId
    private Long id;

    private String plateNo;

    private String vehicleType;

    private BigDecimal capacityTon;

    private String status;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
    @TableLogic
    private Integer deleted;
}
