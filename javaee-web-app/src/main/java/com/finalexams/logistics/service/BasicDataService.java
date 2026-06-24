package com.finalexams.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.finalexams.logistics.entity.Customer;
import com.finalexams.logistics.entity.Driver;
import com.finalexams.logistics.entity.Vehicle;
import com.finalexams.logistics.mapper.CustomerMapper;
import com.finalexams.logistics.mapper.DriverMapper;
import com.finalexams.logistics.mapper.VehicleMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class BasicDataService {

    private final CustomerMapper customerMapper;
    private final DriverMapper driverMapper;
    private final VehicleMapper vehicleMapper;

    public List<Customer> customers() {
        return customerMapper.selectList(new LambdaQueryWrapper<Customer>().orderByAsc(Customer::getName));
    }

    public List<Driver> drivers() {
        return driverMapper.selectList(new LambdaQueryWrapper<Driver>().orderByAsc(Driver::getName));
    }

    public List<Vehicle> vehicles() {
        return vehicleMapper.selectList(new LambdaQueryWrapper<Vehicle>().orderByAsc(Vehicle::getPlateNo));
    }
}
