package com.finalexams.logistics.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("lm_driver")
public class Driver {

    @TableId
    private Long id;

    private String name;

    private String phone;

    private String licenseNo;

    private String status;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
    @TableLogic
    private Integer deleted;
}
