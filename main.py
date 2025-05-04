from ui.vision_ui import VisionEdgeUI

if __name__ == "__main__":
    app = VisionEdgeUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
