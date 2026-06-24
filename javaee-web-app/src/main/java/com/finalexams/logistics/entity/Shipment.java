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
public class Shipment {

    @TableId
    private Long id;

    private String shipmentNo;

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
    @TableLogic
    private Integer deleted;
}
