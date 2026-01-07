import os
import subprocess
import sys
import threading
import argparse
from screens import load as load_screen
from utilities.util_logger import logger
from utilities.util_error_popup import show_error_popup
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QEvent, QTimer, QMetaObject, Qt, Q_ARG
from utilities.util_admin_check import ensure_admin
import preinstall_components.pre_checks as pre_checks
import debloat_components.debloat_execute_raven_scripts as debloat_execute_raven_scripts
import debloat_components.debloat_execute_external_scripts as debloat_execute_external_scripts
import debloat_components.debloat_registry_tweaks as debloat_registry_tweaks
import debloat_components.debloat_configure_updates as debloat_configure_updates
from ui_components.ui_base_full import UIBaseFull
from ui_components.ui_header_text import UIHeaderText
from ui_components.ui_title_text import UITitleText



_INSTALL_UI_BASE = None
DEBLOAT_STEPS = [
    (
        "execute-raven-scripts",
        "Executing debloating scripts...",
        debloat_execute_raven_scripts.main,
    ),
    (
        "execute-external-scripts",
        "Debloating Windows...",
        debloat_execute_external_scripts.main,
    ),
    (
        "registry-tweaks",
        "Making some visual tweaks...",
        debloat_registry_tweaks.main,
    ),
    (
        "configure-updates",
        "Configuring Windows Update policies...",
        debloat_configure_updates.main,
    ),
]



def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Talon Lite installer")
    parser.add_argument(
        "--developer-mode",
        action="store_true",
        help="Run without the installing overlay",
    )
    parser.add_argument(
        "--keep_edge",
        action="keep_edge",
        help="Run without uninstalling Microsoft Edge",
    )
    for slug, _, _ in DEBLOAT_STEPS:
        dest = f"skip_{slug.replace('-', '_')}_step"
        parser.add_argument(
            f"--skip-{slug}-step",
            dest=dest,
            action="store_true",
            help=f"Skip the {slug.replace('-', ' ')} step",
        )
    return parser.parse_args(argv)



def run_screen(module_name: str):
    logger.debug(f"Launching screen: {module_name}")
    try:
        mod = load_screen(module_name)
    except ImportError:
        script_file = f"{module_name}.py"
        script_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'screens',
            script_file
        )
        try:
            subprocess.run([sys.executable, script_path], check=True)
        except Exception as e:
            logger.error(f"Failed to launch screen {script_file}: {e}")
            show_error_popup(
                f"Failed to launch screen '{module_name}'.\n{e}",
                allow_continue=False,
            )
            sys.exit(1)
        return
    try:
        mod.main()
    except SystemExit:
        pass
    except Exception as e:
        logger.exception(f"Exception in screen '{module_name}': {e}")
        show_error_popup(
            f"An unexpected error occurred in screen '{module_name}'.\n{e}",
            allow_continue=False,
        )
        sys.exit(1)



def _build_install_ui():
    app = QApplication.instance() or QApplication(sys.argv)
    base = UIBaseFull()
    for overlay in base.overlays:
        overlay.setWindowOpacity(0.8)
    overlay = base.primary_overlay
    title_label = UITitleText("Talon Lite is installing", parent=overlay)
    UIHeaderText(
        "Please don't use your keyboard or mouse. You can watch as Talon Lite works.",
        parent=overlay,
    )
    status_label = UIHeaderText("", parent=overlay, follow_parent_resize=False)

    class StatusResizer(QObject):
        
        def __init__(self, parent, label, bottom_margin):
            super().__init__(parent)
            self.parent = parent
            self.label = label
            self.bottom_margin = bottom_margin
            parent.installEventFilter(self)
            self._update_position()

        def eventFilter(self, obj, event):
            if obj is self.parent and event.type() == QEvent.Resize:
                self._update_position()
            return False

        def _update_position(self):
            w = self.parent.width()
            fm = self.label.fontMetrics()
            h = fm.height()
            y = self.parent.height() - self.bottom_margin - h
            self.label.setGeometry(0, y, w, h)

    StatusResizer(overlay, status_label, bottom_margin=title_label._top_margin)
    base.show()
    status_label.raise_()
    return app, status_label, base



def _update_status(label: UIHeaderText, message: str):
    if label is None:
        print(message)
    else:
        QMetaObject.invokeMethod(
            label,
            "setText",
            Qt.QueuedConnection,
            Q_ARG(str, message),
        )





def main(argv=None):
    args = parse_args(argv)
    ensure_admin()
    pre_checks.main()
    run_screen('screen_donation_request')
    app = None
    status_label = None
    if not args.developer_mode:
        global _INSTALL_UI_BASE
        app, status_label, _INSTALL_UI_BASE = _build_install_ui()

    def debloat_sequence():
        for slug, message, func in DEBLOAT_STEPS:
            if getattr(args, f"skip_{slug.replace('-', '_')}_step"):
                logger.info(f"Skipping {slug} step")
                continue
            _update_status(status_label, message)
            try:
                if getattr(args, "keep_edge") and slug == "execute-raven-scripts":
                    logger.info("Skipping edge removal")
                    func(keep_edge=True)
                else:
                    func(False)
            except Exception:
                return
        _update_status(status_label, "Restarting system…")
        subprocess.call(["shutdown", "/r", "/t", "0"])

    if args.developer_mode:
        debloat_sequence()
    else:
        def start_thread():
            threading.Thread(target=debloat_sequence, daemon=True).start()
        QTimer.singleShot(0, start_thread)
        sys.exit(app.exec_())



if __name__ == "__main__":
    main()
