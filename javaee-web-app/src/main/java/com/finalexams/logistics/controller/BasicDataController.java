package com.finalexams.logistics.controller;

import com.finalexams.logistics.service.BasicDataService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@RequiredArgsConstructor
/**
 * 基础资料控制器。
 *
 * <p>集中展示客户、司机和车辆数据，供运单管理引用。</p>
 */
public class BasicDataController {

    private final BasicDataService basicDataService;

    @GetMapping("/basic-data")
    /**
     * 基础资料只做展示，不增加额外维护页面，降低课程项目复杂度。
     */
    public String basicData(Model model) {
        model.addAttribute("customers", basicDataService.customers());
        model.addAttribute("drivers", basicDataService.drivers());
        model.addAttribute("vehicles", basicDataService.vehicles());
        return "basic-data";
    }
}
