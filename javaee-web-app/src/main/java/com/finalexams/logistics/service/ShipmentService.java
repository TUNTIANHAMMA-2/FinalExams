package com.finalexams.logistics.service;

import com.finalexams.logistics.entity.Shipment;

import java.util.List;

/**
 * 运单业务接口。
 *
 * <p>Controller 只依赖接口，具体数据库操作由实现类完成。</p>
 */
public interface ShipmentService {

    List<ShipmentView> list(String keyword, String status);

    Shipment getById(Long id);

    Shipment create(Shipment shipment);

    Shipment update(Long id, Shipment shipment);

    void delete(Long id);
}
