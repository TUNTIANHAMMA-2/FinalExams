package com.finalexams.logistics.entity;

import lombok.Getter;

import java.util.Arrays;
import java.util.List;

@Getter
/**
 * 运单状态枚举，集中维护状态编码和页面显示文案，避免散落硬编码。
 */
public enum ShipmentStatus {
    CREATED("CREATED", "待揽收"),
    IN_TRANSIT("IN_TRANSIT", "运输中"),
    DELIVERED("DELIVERED", "已送达"),
    CANCELLED("CANCELLED", "已取消");

    private final String code;
    private final String label;

    ShipmentStatus(String code, String label) {
        this.code = code;
        this.label = label;
    }

    public static List<ShipmentStatus> list() {
        return Arrays.asList(values());
    }

    public static boolean exists(String code) {
        return list().stream().anyMatch(status -> status.code.equals(code));
    }
}
