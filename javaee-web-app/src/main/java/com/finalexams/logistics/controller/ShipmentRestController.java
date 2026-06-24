package com.finalexams.logistics.controller;

import com.finalexams.logistics.common.ApiResponse;
import com.finalexams.logistics.entity.Shipment;
import com.finalexams.logistics.service.ShipmentService;
import com.finalexams.logistics.service.ShipmentView;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/shipments")
@RequiredArgsConstructor
public class ShipmentRestController {

    private final ShipmentService shipmentService;

    @GetMapping
    public ApiResponse<List<ShipmentView>> list(@RequestParam(required = false) String keyword,
                                                @RequestParam(required = false) String status) {
        return ApiResponse.ok(shipmentService.list(keyword, status));
    }

    @GetMapping("/{id}")
    public ApiResponse<Shipment> detail(@PathVariable Long id) {
        return ApiResponse.ok(shipmentService.getById(id));
    }

    @PostMapping
    public ApiResponse<Shipment> create(@Valid @RequestBody Shipment shipment) {
        return ApiResponse.ok(shipmentService.create(shipment));
    }

    @PutMapping("/{id}")
    public ApiResponse<Shipment> update(@PathVariable Long id, @Valid @RequestBody Shipment shipment) {
        return ApiResponse.ok(shipmentService.update(id, shipment));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        shipmentService.delete(id);
        return ApiResponse.ok();
    }
}
