use eframe::egui::{CtxRef, Window};

#[derive(Default)]
pub struct AboutMe;

#[derive(Default)]
pub struct AboutSite;

impl crate::Window for AboutMe {
    fn name(&self) -> &'static str {
        "📚 About Me"
    }

    fn show(&self, ctx: &CtxRef, state: &mut bool) {
        Window::new(self.name())
            .open(state)
            .resizable(false)
            .show(ctx, |ui| {
                ui.vertical_centered_justified(|ui| {
                    ui.label(
                        "Hey I'm Ashwin Vinod, a teenager with \
                     a passion for computers and an ability to learn things quickly. I have been \
                     in the development scene for the past 3 years and I spend most of the time \
                     expanding and improving my current skillset.",
                    );
                    ui.separator();
                    ui.label(
                        "I'm proficient in python and is currently \
                     learning rust. I also have experience in administrating linux systems, \
                     postgresql, mysql, building discord bots and REST APIs.",
                    );
                });
            });
    }
}

impl crate::Window for AboutSite {
    fn name(&self) -> &'static str {
        "📚 About This Website"
    }
    fn show(&self, ctx: &CtxRef, state: &mut bool) {
        Window::new(self.name())
            .open(state)
            .resizable(false)
            .show(ctx, |ui| {
                ui.vertical_centered_justified(|ui| {
                    ui.label(
                        "I initially made my website using css and html but I had no fun \
                while making it and css was a pain for me. I also wanted to add some sort of \
                variety to my website, wanted to make it have a difference.",
                    );
                    ui.separator();
                    ui.label(
                        "Coincidentally, it at was the same time I was learning rust and just \
                discovered egui. I wanted to make a project using egui and rust and it struck my \
                mind to rewrite my website in rust!.",
                    );
                    ui.separator();
                    ui.monospace("This website is written in rust using egui then compiled to \
                    wasm and rendered by WebGL 😉");
                })
            });
    }
}
