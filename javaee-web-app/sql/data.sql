use logistics_db;

insert into lm_customer (id, name, contact_person, phone, address) values
(1, '广州星河电商有限公司', '陈经理', '13800010001', '广州市白云区云城西路88号'),
(2, '深圳南山电子科技有限公司', '李主管', '13800010002', '深圳市南山区科技园'),
(3, '佛山家居供应链有限公司', '周经理', '13800010003', '佛山市顺德区乐从镇');

insert into lm_driver (id, name, phone, license_no, status) values
(1, '王强', '13900020001', 'GD-A10001', '空闲'),
(2, '刘洋', '13900020002', 'GD-A10002', '运输中'),
(3, '赵磊', '13900020003', 'GD-A10003', '空闲');

insert into lm_vehicle (id, plate_no, vehicle_type, capacity_ton, status) values
(1, '粤A-8L256', '厢式货车', 8.00, '可用'),
(2, '粤B-6T918', '冷链货车', 5.00, '运输中'),
(3, '粤E-3K672', '平板货车', 12.00, '可用');

insert into lm_shipment
(id, shipment_no, customer_id, driver_id, vehicle_id, origin_address, destination_address, cargo_name, cargo_weight, freight_fee, status, remark)
values
(1, 'YD202606240001', 1, 1, 1, '广州白云仓', '深圳南山科技园', '电子配件', 3.50, 1800.00, 'CREATED', '普通配送，下午装车'),
(2, 'YD202606240002', 2, 2, 2, '深圳南山仓', '佛山顺德客户点', '冷链食品', 2.80, 2200.00, 'IN_TRANSIT', '全程冷链，注意温控'),
(3, 'YD202606240003', 3, 3, 3, '佛山乐从仓', '广州天河展厅', '办公家具', 6.20, 2600.00, 'DELIVERED', '已签收');
