create database if not exists logistics_db default character set utf8mb4 collate utf8mb4_unicode_ci;
use logistics_db;
set names utf8mb4;

drop table if exists lm_shipment;
drop table if exists lm_vehicle;
drop table if exists lm_driver;
drop table if exists lm_customer;

create table lm_customer (
    id bigint primary key auto_increment comment '客户ID',
    name varchar(80) not null comment '客户名称',
    contact_person varchar(50) not null comment '联系人',
    phone varchar(30) not null comment '联系电话',
    address varchar(200) not null comment '客户地址',
    created_at datetime not null default current_timestamp comment '创建时间',
    updated_at datetime not null default current_timestamp on update current_timestamp comment '更新时间',
    deleted tinyint not null default 0 comment '逻辑删除：0正常，1删除'
) comment '物流客户表';

create table lm_driver (
    id bigint primary key auto_increment comment '司机ID',
    name varchar(50) not null comment '司机姓名',
    phone varchar(30) not null comment '联系电话',
    license_no varchar(60) not null comment '驾驶证号',
    status varchar(20) not null default '空闲' comment '司机状态',
    created_at datetime not null default current_timestamp comment '创建时间',
    updated_at datetime not null default current_timestamp on update current_timestamp comment '更新时间',
    deleted tinyint not null default 0 comment '逻辑删除：0正常，1删除'
) comment '司机信息表';

create table lm_vehicle (
    id bigint primary key auto_increment comment '车辆ID',
    plate_no varchar(20) not null comment '车牌号',
    vehicle_type varchar(40) not null comment '车型',
    capacity_ton decimal(10,2) not null comment '载重吨位',
    status varchar(20) not null default '可用' comment '车辆状态',
    created_at datetime not null default current_timestamp comment '创建时间',
    updated_at datetime not null default current_timestamp on update current_timestamp comment '更新时间',
    deleted tinyint not null default 0 comment '逻辑删除：0正常，1删除',
    unique key uk_vehicle_plate_no (plate_no)
) comment '车辆信息表';

create table lm_shipment (
    id bigint primary key auto_increment comment '运单ID',
    shipment_no varchar(40) not null comment '运单号',
    customer_id bigint not null comment '客户ID',
    driver_id bigint not null comment '司机ID',
    vehicle_id bigint not null comment '车辆ID',
    origin_address varchar(200) not null comment '起点地址',
    destination_address varchar(200) not null comment '终点地址',
    cargo_name varchar(100) not null comment '货物名称',
    cargo_weight decimal(10,2) not null comment '货物重量（吨）',
    freight_fee decimal(10,2) not null comment '运费',
    status varchar(30) not null default 'CREATED' comment '状态：CREATED/IN_TRANSIT/DELIVERED/CANCELLED',
    remark varchar(255) null comment '备注',
    created_at datetime not null default current_timestamp comment '创建时间',
    updated_at datetime not null default current_timestamp on update current_timestamp comment '更新时间',
    deleted tinyint not null default 0 comment '逻辑删除：0正常，1删除',
    unique key uk_shipment_no (shipment_no),
    key idx_shipment_status (status),
    key idx_shipment_customer (customer_id),
    constraint fk_shipment_customer foreign key (customer_id) references lm_customer (id),
    constraint fk_shipment_driver foreign key (driver_id) references lm_driver (id),
    constraint fk_shipment_vehicle foreign key (vehicle_id) references lm_vehicle (id)
) comment '物流运单表';
