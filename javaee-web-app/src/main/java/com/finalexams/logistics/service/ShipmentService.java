package com.finalexams.logistics.service;

import com.finalexams.logistics.entity.Shipment;

import java.util.List;

public interface ShipmentService {

    List<ShipmentView> list(String keyword, String status);

    Shipment getById(Long id);

    Shipment create(Shipment shipment);

    Shipment update(Long id, Shipment shipment);

    void delete(Long id);
}
