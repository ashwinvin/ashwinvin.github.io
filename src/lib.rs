#![forbid(unsafe_code)]
#![cfg_attr(not(debug_assertions), deny(warnings))]
#![warn(clippy::all)]

use std::collections::BTreeSet;

#[cfg(target_arch = "wasm32")]
use eframe::wasm_bindgen::{self, prelude::*};
use eframe::{egui, epi};

mod info;
mod projects;


pub struct MainPage {
    windows: Vec<Box<dyn Window>>,
    visible_windows: BTreeSet<String>,
    window_names: Vec<String>,
}

impl Default for MainPage {
    fn default() -> Self {
        let windows: Vec<Box<dyn crate::Window>> = vec![
            Box::new(info::AboutMe::default()),
            Box::new(info::AboutSite::default()),
            Box::new(projects::ProjectWindow::default()),
        ];
        let mut visible_windows = BTreeSet::new();
        let mut window_names = Vec::new();
        for window in &windows {
            visible_windows.insert(window.name().to_owned());
            window_names.push(window.name().to_owned());
        }
        Self {
            windows,
            visible_windows,
            window_names,
        }
    }
}

fn set_visibilty(visible_windows: &mut BTreeSet<String>, status: bool, key: &'static str) {
    if status {
        visible_windows.insert(key.to_owned());
    } else {
        visible_windows.remove(key);
    }
}

impl epi::App for MainPage {
    fn name(&self) -> &'static str {
        "Ashwin Vinod"
    }

    fn setup(
        &mut self,
        ctx: &egui::CtxRef,
        _frame: &epi::Frame,
        _storage: Option<&dyn epi::Storage>,
    ) {
        ctx.set_visuals(egui::Visuals::dark());
    }

    fn max_size_points(&self) -> egui::Vec2 {
        egui::Vec2::new(f32::INFINITY, f32::INFINITY)
    }

    fn update(&mut self, ctx: &egui::CtxRef, _frame: &epi::Frame) {
        
        for window in &self.windows {
            let mut is_visible = self.visible_windows.contains(window.name());
            window.show(ctx, &mut is_visible);
            set_visibilty(&mut self.visible_windows, is_visible, window.name());
        }
    }
}

pub trait Window {
    fn name(&self) -> &'static str;
    fn show(&self, ctx: &egui::CtxRef, state: &mut bool);
}

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn start(canvas_id: &str) -> Result<(), eframe::wasm_bindgen::JsValue> {
    let app = MainPage::default();
    eframe::start_web(canvas_id, Box::new(app))
}
