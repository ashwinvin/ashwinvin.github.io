use std::collections::HashMap;

use crate::egui::RichText;
use eframe::egui::{CollapsingHeader, CtxRef, Ui, Window};

pub struct Project {
    name: String,
    // repo: String,
    details: HashMap<String, (String, String)>,
}

pub struct ProjectWindow {
    projects: Vec<Project>,
}

impl Default for ProjectWindow {
    fn default() -> Self {
        let projects = vec![Project {
            name: "Visionlib".to_owned(),
            // repo: "https://ashwinvin.github.io/Visionlib/".to_owned(),
            details: HashMap::from([
                (
                    "Documentation:".to_owned(),
                    (
                        "Hosted on github pages".to_owned(),
                        "https://ashwinvin.github.io/Visionlib/".to_owned(),
                    ),
                ),
                (
                    "Source:".to_owned(),
                    (
                        "Available on Github".to_owned(),
                        "https://ashwinvin.github.io/Visionlib/".to_owned(),
                    ),
                ),
                (
                    "Package:".to_owned(),
                    (
                        "Pypi".to_owned(),
                        "https://pypi.org/project/visionlib/".to_owned(),
                    ),
                ),
            ]),
        }];

        Self { projects }
    }
}

impl ProjectWindow {
    fn add_projects(&self, ui: &mut Ui) {
        for project in &self.projects {
            ui.group(|ui| {
                ui.vertical_centered(|ui| {
                    ui.heading(RichText::new(&project.name).strong());
                    ui.separator();
                    ui.label("A simple, easy to use, feature rich, customizable cv library");
                    CollapsingHeader::new("Stats")
                        .id_source(format!("{}-{}", &project.name, "stats"))
                        .show(ui, |ui| {
                            ui.label("Stars: ");
                            ui.label("Forks: ");
                            ui.label("Watchers: ");
                        });
                    CollapsingHeader::new("Details")
                        .id_source(format!("{}-{}", &project.name, "details"))
                        .show(ui, |ui| {
                            for (heading, details) in &project.details {
                                ui.horizontal(|ui| {
                                    ui.label(heading);
                                    ui.hyperlink_to(&details.0, &details.1);
                                });
                            }
                        });
                });
            });
        }
    }
    // fn get_project_data(&self, repo_name: String) {}
}

impl crate::Window for ProjectWindow {
    fn name(&self) -> &'static str {
        "⚡ Projects"
    }

    fn show(&self, ctx: &CtxRef, state: &mut bool) {
        Window::new(RichText::new(self.name()).strong())
            .open(state)
            .resizable(false)
            .show(ctx, |ui| {
                self.add_projects(ui);
                ui.small("More coming soon!");
            });
    }
}
