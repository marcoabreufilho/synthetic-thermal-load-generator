import pandas
import numpy
import matplotlib
import scipy
import customtkinter
import tkinter
import darkdetect
import PIL
import PySide6
import shiboken6
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QScrollArea, QLineEdit, QComboBox, QFormLayout, QGroupBox, QDialog,
    QListWidget, QListWidgetItem, QMessageBox, QInputDialog, QFileDialog, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer
import sys
import os
from core_radiation import generate_radiation
from core_temperature import generate_temperature
import texts
import webbrowser


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def svg_size_from_height(path, height):
    renderer = QSvgRenderer(path)
    viewbox = renderer.viewBoxF()

    if viewbox.height() <= 0:
        width = height
    else:
        width = int(height * viewbox.width() / viewbox.height())

    return width, height


class EditSurfaceDialog(QDialog):
    def __init__(self, surface, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Surface")
        self.surface = surface

        layout = QFormLayout(self)

        self.name_edit = QLineEdit(surface["name"])
        self.azimuth_edit = QLineEdit(str(surface["azimuth"]))
        self.inclination_edit = QLineEdit(str(surface["inclination"]))

        az_row = QHBoxLayout()
        az_row.addWidget(self.azimuth_edit)
        az_info = QLabel("ⓘ")
        az_info.setStyleSheet("color: blue; font-weight: bold;")
        az_info.setToolTip(texts.TOOLTIPS.get("azimuth", ""))
        az_row.addWidget(az_info)

        inc_row = QHBoxLayout()
        inc_row.addWidget(self.inclination_edit)
        inc_info = QLabel("ⓘ")
        inc_info.setStyleSheet("color: blue; font-weight: bold;")
        inc_info.setToolTip(texts.TOOLTIPS.get("inclination", ""))
        inc_row.addWidget(inc_info)

        layout.addRow("Name:", self.name_edit)
        layout.addRow("Azimuth:", az_row)
        layout.addRow("Inclination:", inc_row)

        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def accept(self):
        try:
            self.surface["name"] = self.name_edit.text()
            self.surface["azimuth"] = float(self.azimuth_edit.text())
            self.surface["inclination"] = float(self.inclination_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for azimuth and inclination.")
            return
        super().accept()


class EditReflectedDialog(QDialog):
    def __init__(self, reflected, surfaces, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Reflected")
        self.reflected = reflected
        self.surfaces = surfaces

        layout = QFormLayout(self)

        self.albedo_edit = QLineEdit(str(reflected["albedo"]))
        self.inclination_edit = QLineEdit(str(reflected["inclination"]))
        self.source_combo = QComboBox()

        options = ["Ground"] + [s["name"] for s in surfaces]
        self.source_combo.addItems(options)

        current_source = reflected.get("source", "Ground")
        if current_source in options:
            self.source_combo.setCurrentText(current_source)

        row_alb = QHBoxLayout()
        row_alb.addWidget(self.albedo_edit)
        info_alb = QLabel("ⓘ")
        info_alb.setStyleSheet("color: blue; font-weight: bold;")
        info_alb.setToolTip(texts.TOOLTIPS.get("albedo", ""))
        row_alb.addWidget(info_alb)
        layout.addRow("Albedo:", row_alb)

        row_inc = QHBoxLayout()
        row_inc.addWidget(self.inclination_edit)
        info_inc = QLabel("ⓘ")
        info_inc.setStyleSheet("color: blue; font-weight: bold;")
        info_inc.setToolTip(texts.TOOLTIPS.get("inclination", ""))
        row_inc.addWidget(info_inc)
        layout.addRow("Inclination:", row_inc)

        row_source = QHBoxLayout()
        row_source.addWidget(self.source_combo)
        info_source = QLabel("ⓘ")
        info_source.setStyleSheet("color: blue; font-weight: bold;")
        info_source.setToolTip(texts.TOOLTIPS.get("source", ""))
        row_source.addWidget(info_source)
        layout.addRow("Source:", row_source)

        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def accept(self):
        try:
            self.reflected["albedo"] = float(self.albedo_edit.text())
            self.reflected["inclination"] = float(self.inclination_edit.text())
            self.reflected["source"] = self.source_combo.currentText()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for albedo and inclination.")
            return
        super().accept()


class SurfaceDialog(QDialog):
    def __init__(self, surfaces, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inclined Surfaces")
        self.surfaces = surfaces
        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.edit_surface)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Surface")
        add_btn.clicked.connect(self.add_surface)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_surface)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_surface)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.update_list()

    def update_list(self):
        self.list_widget.clear()
        for s in self.surfaces:
            self.list_widget.addItem(f"{s['name']} - Azimuth: {s['azimuth']}° - Inclination: {s['inclination']}°")

    def add_surface(self):
        if len(self.surfaces) >= 10:
            QMessageBox.warning(self, "Limit", "Maximum 10 surfaces allowed.")
            return
        new_surface = {"name": f"Surf {len(self.surfaces)+1}", "azimuth": 0, "inclination": 0}
        dlg = EditSurfaceDialog(new_surface, self)
        if dlg.exec():
            self.surfaces.append(new_surface)
            self.update_list()

    def edit_surface(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        dlg = EditSurfaceDialog(self.surfaces[row], self)
        if dlg.exec():
            self.update_list()

    def delete_surface(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            del self.surfaces[row]
            self.update_list()


class ReflectedDialog(QDialog):
    def __init__(self, surfaces, reflected_surfaces, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reflected Radiation")
        self.surfaces = surfaces
        self.reflected_surfaces = reflected_surfaces

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.edit_surface)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Reflected Surface")
        add_btn.clicked.connect(self.add_surface)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_surface)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_surface)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.update_list()

    def update_list(self):
        self.list_widget.clear()
        for s in self.reflected_surfaces:
            self.list_widget.addItem(
                f"{s['name']} - Albedo: {s['albedo']} - Inclination: {s['inclination']}° - Source: {s['source']}"
            )

    def add_surface(self):
        options = ["Bottom Surface"] + [s["name"] for s in self.surfaces]
        name, ok = QInputDialog.getItem(self, "Surface", "Select Surface:", options, editable=False)
        if ok:
            count = sum(1 for s in self.reflected_surfaces if s["name"].startswith("Bottom Surface"))
            if name == "Bottom Surface":
                display_name = "Bottom Surface" if count == 0 else f"Bottom Surface_{count + 1}"
            else:
                display_name = name

            new_ref = {"name": display_name, "albedo": 0, "inclination": 0, "source": "Ground"}
            dlg = EditReflectedDialog(new_ref, self.surfaces, self)
            if dlg.exec():
                self.reflected_surfaces.append(new_ref)
                self.update_list()

    def edit_surface(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        dlg = EditReflectedDialog(self.reflected_surfaces[row], self.surfaces, self)
        if dlg.exec():
            self.update_list()

    def delete_surface(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            del self.reflected_surfaces[row]
            self.update_list()


class ThermalLoadApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synthetic Thermal Load Generator")
        self.setWindowIcon(QIcon(resource_path("assets/SL_ICO.ico")))
        self.layout = QVBoxLayout(self)
        self.resize(550, 750)
        self.setMinimumSize(550, 750)

        screen = QApplication.primaryScreen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

        title = QLabel("Synthetic Thermal Load Generator")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(title)

        self.checkbox_radiation = QCheckBox("Solar Radiation")
        self.checkbox_temperature = QCheckBox("Air Shade Temperature")

        self.checkbox_radiation.toggled.connect(self.update_fields_state)
        self.checkbox_temperature.toggled.connect(self.update_fields_state)

        self.layout.addWidget(self.checkbox_radiation)

        self.input_fields = {}
        self.surfaces = []
        self.reflected_surfaces = []

        self.scroll_area_radiation = QScrollArea()
        self.scroll_widget_radiation = QWidget()
        self.scroll_layout_radiation = QVBoxLayout(self.scroll_widget_radiation)
        self.scroll_area_radiation.setWidgetResizable(True)
        self.scroll_area_radiation.setWidget(self.scroll_widget_radiation)
        self.layout.addWidget(self.scroll_area_radiation)

        self.group_radiation = QGroupBox("Solar Radiation Settings")
        self.layout_radiation = QFormLayout(self.group_radiation)
        self._add_radiation_fields()
        self.scroll_layout_radiation.addWidget(self.group_radiation)

        self.layout.addWidget(self.checkbox_temperature)

        self.scroll_area_temperature = QScrollArea()
        self.scroll_widget_temperature = QWidget()
        self.scroll_layout_temperature = QVBoxLayout(self.scroll_widget_temperature)
        self.scroll_area_temperature.setWidgetResizable(True)
        self.scroll_area_temperature.setWidget(self.scroll_widget_temperature)
        self.layout.addWidget(self.scroll_area_temperature)

        self.group_temp = QGroupBox("Air Shade Temperature Settings")
        self.layout_temp = QFormLayout(self.group_temp)
        self._add_temperature_fields()
        self.scroll_layout_temperature.addWidget(self.group_temp)

        row_layout1 = QHBoxLayout()
        self.btn_surfaces = QPushButton("Inclined Surfaces")
        self.btn_surfaces.clicked.connect(self.manage_surfaces)
        info1 = QLabel("ⓘ")
        info1.setStyleSheet("color: blue; font-weight: bold;")
        info1.setToolTip(texts.TOOLTIPS.get("inclined", ""))
        row_layout1.addWidget(self.btn_surfaces)
        row_layout1.addWidget(info1)
        self.layout_radiation.addRow(row_layout1)

        row_layout2 = QHBoxLayout()
        self.btn_reflected = QPushButton("Reflected Radiation")
        self.btn_reflected.clicked.connect(self.manage_reflected)
        info2 = QLabel("ⓘ")
        info2.setStyleSheet("color: blue; font-weight: bold;")
        info2.setToolTip(texts.TOOLTIPS.get("reflected", ""))
        row_layout2.addWidget(self.btn_reflected)
        row_layout2.addWidget(info2)
        self.layout_radiation.addRow(row_layout2)

        row_shadowing = QHBoxLayout()
        self.checkbox_self_shadowing = QCheckBox("Generate Solar Position Inputs for Self-Shadowing Analysis")
        info_shadowing = QLabel("ⓘ")
        info_shadowing.setStyleSheet("color: blue; font-weight: bold;")
        info_shadowing.setToolTip(texts.TOOLTIPS.get("self_shadowing", ""))
        row_shadowing.addWidget(self.checkbox_self_shadowing)
        row_shadowing.addWidget(info_shadowing)
        self.layout_radiation.addRow(row_shadowing)

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate)
        self.layout.addWidget(self.generate_button)

        logos_frame = QFrame()
        logos_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
            }
        """)

        logos_layout = QHBoxLayout(logos_frame)
        logos_layout.setContentsMargins(0, 0, 0, 0)
        logos_layout.setSpacing(10)
        logos_layout.setAlignment(Qt.AlignCenter)

        isise_w, isise_h = svg_size_from_height(resource_path("logos/isise.svg"), 70)
        fct_w, fct_h = svg_size_from_height(resource_path("logos/fct.svg"), 50)
        uminho_w, uminho_h = svg_size_from_height(resource_path("logos/uminho.svg"), 85)

        self.logo_isise = QSvgWidget(resource_path("logos/isise.svg"))
        self.logo_isise.setFixedSize(isise_w, isise_h)

        self.logo_fct = QSvgWidget(resource_path("logos/fct.svg"))
        self.logo_fct.setFixedSize(fct_w, fct_h)

        self.logo_uminho = QSvgWidget(resource_path("logos/uminho.svg"))
        self.logo_uminho.setFixedSize(uminho_w, uminho_h)

        logos_layout.addWidget(self.logo_isise)
        logos_layout.addWidget(self.logo_fct)
        logos_layout.addWidget(self.logo_uminho)

        self.layout.addWidget(logos_frame)

        links_layout = QHBoxLayout()
        self.support_btn = QPushButton("View Supporting Publication")
        self.support_btn.setToolTip(texts.TOOLTIPS.get("supporting", ""))
        self.support_btn.clicked.connect(self.open_supporting_publication)
        links_layout.addWidget(self.support_btn)

        self.report_btn = QPushButton("Contact && Feedback")
        self.report_btn.setToolTip(texts.TOOLTIPS.get("report", ""))
        self.report_btn.clicked.connect(self.open_report_results)
        links_layout.addWidget(self.report_btn)

        self.layout.addLayout(links_layout)

        self.update_fields_state()

    def _add_radiation_fields(self):
        self._add_field(self.layout_radiation, "latitude", "Latitude:")
        self._add_field(self.layout_radiation, "longitude", "Longitude:")
        self._add_dropdown(self.layout_radiation, "time_zone", "Time Zone:", texts.TIME_ZONES)
        self._add_field(self.layout_radiation, "solar_constant", "Solar Constant (W/m²):", str(texts.SOLAR_CONSTANT))
        self._add_field(self.layout_radiation, "kt_cooling", "Clearness Index (Cooling):", str(texts.KT_COOLING))
        self._add_field(self.layout_radiation, "kt_heating", "Clearness Index (Heating):", str(texts.KT_HEATING))
        self._add_field(self.layout_radiation, "interval_radiation", "Interval (seconds) for Radiation:")

    def _add_temperature_fields(self):
        self._add_field(self.layout_temp, "min_temp", "Minimum Temperature (°C):")
        self._add_field(self.layout_temp, "max_temp", "Maximum Temperature (°C):")
        self._add_field(self.layout_temp, "daily_variation", "Daily Temperature Variation (°C):")
        self._add_field(self.layout_temp, "interval_temperature", "Interval (seconds) for Temperature:")

    def _add_field(self, layout, key, label_text, default_value=""):
        row = QHBoxLayout()
        label = QLabel(label_text)
        edit = QLineEdit()
        edit.setText(default_value)
        row.addWidget(edit)
        info = QLabel("ⓘ")
        info.setStyleSheet("color: blue; font-weight: bold;")
        info.setToolTip(texts.TOOLTIPS.get(key, ""))
        row.addWidget(info)
        layout.addRow(label, row)
        self.input_fields[key] = edit

    def _add_dropdown(self, layout, key, label_text, options):
        row = QHBoxLayout()
        label = QLabel(label_text)
        combo = QComboBox()
        combo.addItems(options)
        if key == "time_zone":
            combo.setCurrentIndex(12)
        row.addWidget(combo)
        info = QLabel("ⓘ")
        info.setStyleSheet("color: blue; font-weight: bold;")
        info.setToolTip(texts.TOOLTIPS.get(key, ""))
        row.addWidget(info)
        layout.addRow(label, row)
        self.input_fields[key] = combo

    def update_fields_state(self):
        enable_radiation = self.checkbox_radiation.isChecked()
        for key in ["latitude", "longitude", "time_zone", "solar_constant", "kt_cooling", "kt_heating", "interval_radiation"]:
            widget = self.input_fields[key]
            widget.setEnabled(enable_radiation)
        self.btn_surfaces.setEnabled(enable_radiation)
        self.btn_reflected.setEnabled(enable_radiation)
        self.checkbox_self_shadowing.setEnabled(enable_radiation)

        enable_temp = self.checkbox_temperature.isChecked()
        for key in ["min_temp", "max_temp", "daily_variation", "interval_temperature"]:
            widget = self.input_fields[key]
            widget.setEnabled(enable_temp)

    def generate(self):
        missing = []
        if self.checkbox_radiation.isChecked():
            for key in ["latitude", "longitude", "solar_constant", "kt_cooling", "kt_heating", "interval_radiation"]:
                if not self.input_fields[key].text():
                    missing.append(key)
        if self.checkbox_temperature.isChecked():
            for key in ["min_temp", "max_temp", "daily_variation", "interval_temperature"]:
                if not self.input_fields[key].text():
                    missing.append(key)

        if missing:
            QMessageBox.warning(self, "Missing Fields", f"Please fill all required fields: {', '.join(missing)}")
            return

        try:
            if self.checkbox_radiation.isChecked():
                latitude = float(self.input_fields["latitude"].text())
                longitude = float(self.input_fields["longitude"].text())
                solar_constant = float(self.input_fields["solar_constant"].text())
                kt_cooling = float(self.input_fields["kt_cooling"].text())
                kt_heating = float(self.input_fields["kt_heating"].text())
                interval_radiation = float(self.input_fields["interval_radiation"].text())

                time_zone_str = self.input_fields["time_zone"].currentText()
                time_zone_raw = time_zone_str.split("UTC")[1].split(" ")[0].replace("±", "0")
                time_zone = float(time_zone_raw)

            if self.checkbox_temperature.isChecked():
                min_temp = float(self.input_fields["min_temp"].text())
                max_temp = float(self.input_fields["max_temp"].text())
                daily_variation = float(self.input_fields["daily_variation"].text())
                interval_seconds = float(self.input_fields["interval_temperature"].text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values in all fields.")
            return

        if not self.checkbox_radiation.isChecked() and not self.checkbox_temperature.isChecked():
            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select at least one option: Solar Radiation or Air Shade Temperature."
            )
            return

        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not folder:
            return

        if self.checkbox_radiation.isChecked():
            generate_radiation(
                folder, latitude, longitude, time_zone, solar_constant, kt_heating,
                kt_cooling, interval_radiation, self.surfaces, self.reflected_surfaces,
                generate_self_shadowing_inputs=self.checkbox_self_shadowing.isChecked()
            )

        if self.checkbox_temperature.isChecked():
            generate_temperature(folder, min_temp, max_temp, daily_variation, interval_seconds)

    def manage_surfaces(self):
        dialog = SurfaceDialog(self.surfaces, self)
        dialog.exec()

    def manage_reflected(self):
        dialog = ReflectedDialog(self.surfaces, self.reflected_surfaces, self)
        dialog.exec()

    def open_supporting_publication(self):
        if texts.SUPPORTING_PUBLICATION_LINK:
            webbrowser.open(texts.SUPPORTING_PUBLICATION_LINK)

    def open_report_results(self):
        if texts.REPORT_RESULTS_LINK:
            webbrowser.open(texts.REPORT_RESULTS_LINK)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThermalLoadApp()
    window.show()
    sys.exit(app.exec())