package com.finalexams.logistics.service.impl;

import com.finalexams.logistics.entity.Shipment;
import com.finalexams.logistics.entity.ShipmentStatus;
import com.finalexams.logistics.mapper.ShipmentMapper;
import com.finalexams.logistics.service.ShipmentService;
import com.finalexams.logistics.service.ShipmentView;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ShipmentServiceImpl implements ShipmentService {

    private final ShipmentMapper shipmentMapper;

    @Override
    public List<ShipmentView> list(String keyword, String status) {
        return shipmentMapper.selectShipmentViews(keyword, status);
    }

    @Override
    public Shipment getById(Long id) {
        Shipment shipment = shipmentMapper.selectById(id);
        if (shipment == null) {
            throw new IllegalArgumentException("运单不存在");
        }
        return shipment;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Shipment create(Shipment shipment) {
        LocalDateTime now = LocalDateTime.now();
        shipment.setId(null);
        shipment.setShipmentNo(generateShipmentNo(now));
        normalizeStatus(shipment);
        validateStatus(shipment.getStatus());
        shipment.setCreatedAt(now);
        shipment.setUpdatedAt(now);
        shipment.setDeleted(0);
        shipmentMapper.insert(shipment);
        return shipment;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Shipment update(Long id, Shipment form) {
        Shipment existing = getById(id);
        normalizeStatus(form);
        validateStatus(form.getStatus());
        existing.setCustomerId(form.getCustomerId());
        existing.setDriverId(form.getDriverId());
        existing.setVehicleId(form.getVehicleId());
        existing.setOriginAddress(form.getOriginAddress());
        existing.setDestinationAddress(form.getDestinationAddress());
        existing.setCargoName(form.getCargoName());
        existing.setCargoWeight(form.getCargoWeight());
        existing.setFreightFee(form.getFreightFee());
        existing.setStatus(form.getStatus());
        existing.setRemark(form.getRemark());
        existing.setUpdatedAt(LocalDateTime.now());
        shipmentMapper.updateById(existing);
        return existing;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void delete(Long id) {
        getById(id);
        shipmentMapper.deleteById(id);
    }

    private String generateShipmentNo(LocalDateTime now) {
        return "YD" + now.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
    }

    private void validateStatus(String status) {
        if (status == null || !ShipmentStatus.exists(status)) {
            throw new IllegalArgumentException("运单状态不合法");
        }
    }

    private void normalizeStatus(Shipment shipment) {
        if (shipment.getStatus() == null || shipment.getStatus().isBlank()) {
            shipment.setStatus(ShipmentStatus.CREATED.getCode());
        }
    }
}
