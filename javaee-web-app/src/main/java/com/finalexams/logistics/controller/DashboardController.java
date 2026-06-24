package com.finalexams.logistics.controller;

import com.finalexams.logistics.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping({"/", "/dashboard"})
    public String dashboard(Model model) {
        model.addAttribute("overview", dashboardService.overview());
        model.addAttribute("statusCounts", dashboardService.shipmentStatusCounts());
        return "dashboard";
    }
}
