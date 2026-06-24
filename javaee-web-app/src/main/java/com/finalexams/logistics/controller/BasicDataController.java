package com.finalexams.logistics.controller;

import com.finalexams.logistics.service.BasicDataService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@RequiredArgsConstructor
public class BasicDataController {

    private final BasicDataService basicDataService;

    @GetMapping("/basic-data")
    public String basicData(Model model) {
        model.addAttribute("customers", basicDataService.customers());
        model.addAttribute("drivers", basicDataService.drivers());
        model.addAttribute("vehicles", basicDataService.vehicles());
        return "basic-data";
    }
}
