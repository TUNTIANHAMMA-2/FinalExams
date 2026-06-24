package com.finalexams.logistics.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("lm_shipment")
/**
 * 运单实体，是系统核心业务对象，对应数据库 lm_shipment 表。
 */
public class Shipment {

    @TableId
    private Long id;

    private String shipmentNo;

    /**
     * 通过客户、司机、车辆 ID 建立运单与基础资料之间的关联。
     */
    @NotNull(message = "不能为空")
    private Long customerId;

    @NotNull(message = "不能为空")
    private Long driverId;

    @NotNull(message = "不能为空")
    private Long vehicleId;

    @NotBlank(message = "不能为空")
    private String originAddress;

    @NotBlank(message = "不能为空")
    private String destinationAddress;

    @NotBlank(message = "不能为空")
    private String cargoName;

    @NotNull(message = "不能为空")
    @DecimalMin(value = "0.01", message = "必须大于0")
    private BigDecimal cargoWeight;

    @NotNull(message = "不能为空")
    @DecimalMin(value = "0.00", message = "不能小于0")
    private BigDecimal freightFee;

    private String status;

    private String remark;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    /**
     * 逻辑删除字段：删除运单时保留数据记录，便于课程中说明 MyBatis-Plus 特性。
     */
    @TableLogic
    private Integer deleted;
}
