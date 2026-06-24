package com.finalexams.logistics.controller;

import com.finalexams.logistics.entity.Shipment;
import com.finalexams.logistics.entity.ShipmentStatus;
import com.finalexams.logistics.service.BasicDataService;
import com.finalexams.logistics.service.ShipmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/shipments")
@RequiredArgsConstructor
public class ShipmentPageController {

    private final ShipmentService shipmentService;
    private final BasicDataService basicDataService;

    @GetMapping
    public String list(@RequestParam(required = false) String keyword,
                       @RequestParam(required = false) String status,
                       Model model) {
        model.addAttribute("shipments", shipmentService.list(keyword, status));
        model.addAttribute("keyword", keyword);
        model.addAttribute("selectedStatus", status);
        model.addAttribute("statuses", ShipmentStatus.list());
        return "shipments/list";
    }

    @GetMapping("/new")
    public String createForm(Model model) {
        model.addAttribute("shipment", new Shipment());
        prepareForm(model, "新增运单", "/shipments");
        return "shipments/form";
    }

    @PostMapping
    public String create(@Valid @ModelAttribute Shipment shipment,
                         BindingResult bindingResult,
                         Model model,
                         RedirectAttributes redirectAttributes) {
        if (bindingResult.hasErrors()) {
            prepareForm(model, "新增运单", "/shipments");
            return "shipments/form";
        }
        shipmentService.create(shipment);
        redirectAttributes.addFlashAttribute("message", "运单创建成功");
        return "redirect:/shipments";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        model.addAttribute("shipment", shipmentService.getById(id));
        prepareForm(model, "编辑运单", "/shipments/" + id);
        return "shipments/form";
    }

    @PostMapping("/{id}")
    public String update(@PathVariable Long id,
                         @Valid @ModelAttribute Shipment shipment,
                         BindingResult bindingResult,
                         Model model,
                         RedirectAttributes redirectAttributes) {
        if (bindingResult.hasErrors()) {
            shipment.setId(id);
            prepareForm(model, "编辑运单", "/shipments/" + id);
            return "shipments/form";
        }
        shipmentService.update(id, shipment);
        redirectAttributes.addFlashAttribute("message", "运单更新成功");
        return "redirect:/shipments";
    }

    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id, RedirectAttributes redirectAttributes) {
        shipmentService.delete(id);
        redirectAttributes.addFlashAttribute("message", "运单删除成功");
        return "redirect:/shipments";
    }

    private void prepareForm(Model model, String title, String action) {
        model.addAttribute("title", title);
        model.addAttribute("action", action);
        model.addAttribute("customers", basicDataService.customers());
        model.addAttribute("drivers", basicDataService.drivers());
        model.addAttribute("vehicles", basicDataService.vehicles());
        model.addAttribute("statuses", ShipmentStatus.list());
    }
}
