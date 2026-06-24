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
/**
 * 运单 REST 控制器。
 *
 * <p>覆盖 GET、POST、PUT、DELETE，体现 RESTful 接口开发要求。</p>
 */
public class ShipmentRestController {

    private final ShipmentService shipmentService;

    @GetMapping
    /**
     * 使用 {@code @RequestParam} 接收查询参数，可按关键字和状态筛选运单。
     */
    public ApiResponse<List<ShipmentView>> list(@RequestParam(required = false) String keyword,
                                                @RequestParam(required = false) String status) {
        return ApiResponse.ok(shipmentService.list(keyword, status));
    }

    @GetMapping("/{id}")
    /**
     * 使用 {@code @PathVariable} 接收路径中的运单 ID。
     */
    public ApiResponse<Shipment> detail(@PathVariable Long id) {
        return ApiResponse.ok(shipmentService.getById(id));
    }

    @PostMapping
    /**
     * 使用 {@code @RequestBody} 接收 JSON 请求体，{@code @Valid} 触发实体字段校验。
     */
    public ApiResponse<Shipment> create(@Valid @RequestBody Shipment shipment) {
        return ApiResponse.ok(shipmentService.create(shipment));
    }

    @PutMapping("/{id}")
    /**
     * PUT 用于更新已有运单，路径 ID 决定要修改的数据。
     */
    public ApiResponse<Shipment> update(@PathVariable Long id, @Valid @RequestBody Shipment shipment) {
        return ApiResponse.ok(shipmentService.update(id, shipment));
    }

    @DeleteMapping("/{id}")
    /**
     * MyBatis-Plus 根据实体上的 {@code @TableLogic} 执行逻辑删除。
     */
    public ApiResponse<Void> delete(@PathVariable Long id) {
        shipmentService.delete(id);
        return ApiResponse.ok();
    }
}
