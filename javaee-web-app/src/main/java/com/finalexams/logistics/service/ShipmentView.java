package com.finalexams.logistics.service;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
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
