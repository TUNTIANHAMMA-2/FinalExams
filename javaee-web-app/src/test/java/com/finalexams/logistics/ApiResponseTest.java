package com.finalexams.logistics;

import com.finalexams.logistics.common.ApiResponse;
import com.finalexams.logistics.entity.ShipmentStatus;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class ApiResponseTest {

    @Test
    void okResponseContainsCodeMessageAndData() {
        ApiResponse<String> response = ApiResponse.ok("demo");

        assertThat(response.getCode()).isEqualTo(200);
        assertThat(response.getMessage()).isEqualTo("success");
        assertThat(response.getData()).isEqualTo("demo");
    }

    @Test
    void shipmentStatusValidatesKnownCodes() {
        assertThat(ShipmentStatus.exists("CREATED")).isTrue();
        assertThat(ShipmentStatus.exists("UNKNOWN")).isFalse();
    }
}
