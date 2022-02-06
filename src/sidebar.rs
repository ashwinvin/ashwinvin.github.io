use std::collections::BTreeSet;

use eframe::egui::{CtxRef, RichText, ScrollArea, SidePanel};

#[derive(Default)]
pub struct SideBar;

impl SideBar {
    pub fn show(ctx: &CtxRef, windows: &[String], visible_windows: &mut BTreeSet<String>) {
        SidePanel::left("left_panel").show(ctx, |ui| {
            ui.heading(RichText::new("👋 Ashwin Vinod").strong());
            ui.separator();
            ScrollArea::vertical().show(ui, |ui| {
                ui.label(RichText::new("Windows:").strong());
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
