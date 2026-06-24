package com.finalexams.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.finalexams.logistics.entity.Shipment;
import com.finalexams.logistics.entity.ShipmentStatus;
import com.finalexams.logistics.mapper.CustomerMapper;
import com.finalexams.logistics.mapper.DriverMapper;
import com.finalexams.logistics.mapper.ShipmentMapper;
import com.finalexams.logistics.mapper.VehicleMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
/**
 * 工作台服务，聚合各业务表数量，给首页统计卡片和状态分布使用。
 */
public class DashboardService {

    private final CustomerMapper customerMapper;
    private final DriverMapper driverMapper;
    private final VehicleMapper vehicleMapper;
    private final ShipmentMapper shipmentMapper;

    public Map<String, Long> overview() {
        Map<String, Long> data = new LinkedHashMap<>();
        data.put("客户数量", customerMapper.selectCount(null));
        data.put("司机数量", driverMapper.selectCount(null));
        data.put("车辆数量", vehicleMapper.selectCount(null));
        data.put("运单数量", shipmentMapper.selectCount(null));
        return data;
    }

    public Map<String, Long> shipmentStatusCounts() {
        Map<String, Long> data = new LinkedHashMap<>();
        for (ShipmentStatus status : ShipmentStatus.list()) {
            Long count = shipmentMapper.selectCount(new LambdaQueryWrapper<Shipment>()
                    .eq(Shipment::getStatus, status.getCode()));
            data.put(status.getLabel(), count);
        }
        return data;
    }
}
