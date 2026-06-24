package com.finalexams.logistics.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.finalexams.logistics.entity.Shipment;
import com.finalexams.logistics.service.ShipmentView;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface ShipmentMapper extends BaseMapper<Shipment> {

    @Select("""
            select s.*, c.name as customer_name, d.name as driver_name, v.plate_no as vehicle_plate_no
            from lm_shipment s
            left join lm_customer c on c.id = s.customer_id and c.deleted = 0
            left join lm_driver d on d.id = s.driver_id and d.deleted = 0
            left join lm_vehicle v on v.id = s.vehicle_id and v.deleted = 0
            where s.deleted = 0
              and (#{keyword} is null or #{keyword} = ''
                   or s.shipment_no like concat('%', #{keyword}, '%')
                   or s.cargo_name like concat('%', #{keyword}, '%')
                   or c.name like concat('%', #{keyword}, '%'))
              and (#{status} is null or #{status} = '' or s.status = #{status})
            order by s.created_at desc
            """)
    List<ShipmentView> selectShipmentViews(@Param("keyword") String keyword, @Param("status") String status);
}
