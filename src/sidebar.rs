use std::collections::BTreeSet;

use eframe::egui;

#[derive(Default)]
pub struct SideBar;

impl SideBar {
    pub fn show(ctx: &egui::CtxRef, windows: &[String], visible_windows: &mut BTreeSet<String>) {
        egui::SidePanel::left("left_panel").show(ctx, |ui| {
            ui.heading("👋 Ashwin Vinod");
            ui.separator();
            egui::ScrollArea::vertical().show(ui, |ui| {
                ui.label("Windows:");
                for window in windows {
                    let mut checked = visible_windows.contains(window);
                    ui.checkbox(&mut checked, window);
                    if checked {
                        visible_windows.insert(window.to_string());
                    } else {
                        visible_windows.remove(window);
                    }
                }
                ui.separator();
                if ui.button("Organize Windows").clicked() {
                    ctx.memory().reset_areas();
                }
            });
        });
    }
}
