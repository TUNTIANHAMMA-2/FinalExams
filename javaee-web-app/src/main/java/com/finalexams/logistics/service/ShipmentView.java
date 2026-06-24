package com.finalexams.logistics.service;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
/**
 * 运单列表视图对象。
 *
 * <p>封装关联查询后的展示字段，不直接污染数据库实体类。</p>
 */
public class ShipmentView {

    private Long id;
    private String shipmentNo;
    private Long customerId;
    private Long driverId;
    private Long vehicleId;
    private String customerName;
    private String driverName;
    private String vehiclePlateNo;
    private String originAddress;
    private String destinationAddress;
    private String cargoName;
    private BigDecimal cargoWeight;
    private BigDecimal freightFee;
    private String status;
    private String remark;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
