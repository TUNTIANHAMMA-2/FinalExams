package com.finalexams.logistics.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("lm_customer")
/**
 * 客户实体，对应数据库 lm_customer 表，用于保存物流委托方信息。
 */
public class Customer {

    @TableId
    private Long id;

    private String name;

    private String contactPerson;

    private String phone;

    private String address;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @TableLogic
    private Integer deleted;
}
