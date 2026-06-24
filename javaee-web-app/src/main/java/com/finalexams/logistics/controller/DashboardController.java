package com.finalexams.logistics.controller;

import com.finalexams.logistics.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@RequiredArgsConstructor
/**
 * 首页控制器。
 *
 * <p>负责展示系统总览数据，适合作为答辩演示的第一个页面。</p>
 */
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping({"/", "/dashboard"})
    /**
     * 查询统计数据并渲染 Thymeleaf 工作台页面。
     */
    public String dashboard(Model model) {
        model.addAttribute("overview", dashboardService.overview());
        model.addAttribute("statusCounts", dashboardService.shipmentStatusCounts());
        return "dashboard";
    }
}
