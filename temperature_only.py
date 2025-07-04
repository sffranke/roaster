import argparse
import serial
import time
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons
import numpy as np
import random

class LiveRoastPlot:
    def __init__(self, ser, profiles, initial_profile):
        self.ser = ser
        self.profiles = profiles
        # Keys und Longnames für Profilauswahl
        self.keys = list(self.profiles.keys())
        self.longnames = [self.profiles[k]["longname"] for k in self.keys]
        self.current_profile = initial_profile

        # Datenpuffer und Zeitbasis
        self.start_time = time.time()
        self.zeiten = []
        self.temperaturen = []
        self.max_x = 20

        # Figure & Achsen, Platz für Widgets rechts schaffen
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(right=0.75)

        # Referenzkurve(n) und Live-Kurve initial zeichnen
        self.ref_lines = []
        self.plot_reference()
        self.line, = self.ax.plot([], [], 'r-', label='Live-Daten')

        # Achsen, Beschriftung, Limits, Grid, Ticks
        self.ax.set_xlim(0, self.max_x)
        self.ax.set_ylim(0, 250)
        self.ax.set_xlabel('Zeit (min)')
        self.ax.set_ylabel('Temperatur (°C)')
        self.ax.set_yticks(range(0, 251, 10))
        self.ax.grid(which='major', linestyle='--', alpha=0.7)
        self.set_x_ticks = lambda xmax: (
            self.ax.set_xlim(0, xmax),
            self.ax.set_xticks(range(0, xmax + 1))
        )

        # Legende, Mittelwert-Text und Zeit-Text (mm:ss)
        self.leg = self.ax.legend(loc='upper left')
        self.mean_text = self.ax.text(
            1.02, 1.00, "", transform=self.ax.transAxes,
            fontsize=12, fontweight='bold', color='blue',
            va='top', ha='left'
        )
        self.time_text = self.ax.text(
            1.02, 0.92, "", transform=self.ax.transAxes,
            fontsize=10, color='black',
            va='top', ha='left'
        )

        # Reset-Button
        reset_ax = self.fig.add_axes([0.80, 0.05, 0.15, 0.05])
        self.reset_button = Button(reset_ax, 'Reset')
        self.reset_button.on_clicked(self.on_reset)

        # Profilauswahl per RadioButtons
        radio_ax = self.fig.add_axes([0.80, 0.15, 0.15, 0.35],
                                     facecolor='lightgoldenrodyellow')
        init_index = self.keys.index(self.current_profile)
        self.radio = RadioButtons(radio_ax, self.longnames, active=init_index)
        self.radio.on_clicked(self.on_profile_change)

    def plot_reference(self):
        # Alte Referenzlinien entfernen
        for ln in self.ref_lines:
            ln.remove()
        self.ref_lines.clear()

        # Neue Referenzkurven zeichnen
        if self.current_profile == "a":
            for key in self.keys:
                prof = self.profiles[key]
                ln, = self.ax.plot(prof["times"], prof["temps"], '--',
                                   label=prof["longname"])
                self.ref_lines.append(ln)
        else:
            prof = self.profiles[self.current_profile]
            ln, = self.ax.plot(prof["times"], prof["temps"], 'g--',
                               label=prof["longname"])
            self.ref_lines.append(ln)

        # Legende aktualisieren
        self.leg = self.ax.legend(loc='upper left')

    def on_reset(self, event):
        """Zeitbasis und Datenpuffer zurücksetzen."""
        self.start_time = time.time()
        self.zeiten.clear()
        self.temperaturen.clear()
        self.max_x = 20
        self.set_x_ticks(self.max_x)
        self.line.set_data([], [])
        self.mean_text.set_text("")
        self.time_text.set_text("")
        plt.draw()

    def on_profile_change(self, longname):
        """Profilwechsel über Longname."""
        idx = self.longnames.index(longname)
        self.current_profile = self.keys[idx]
        self.plot_reference()
        plt.draw()

    def run(self):
        """Hauptloop: seriell lesen oder Demo simulieren, Plot updaten."""
        demo_mode = (self.ser is None)

        try:
            while True:
                # Zeit seit Start
                elapsed_sec = time.time() - self.start_time
                elapsed_min = elapsed_sec / 60.0

                if not demo_mode:
                    raw = self.ser.readline().decode('utf-8').strip()
                    if not raw:
                        continue
                    try:
                        temp = float(raw) - 1.7
                    except ValueError:
                        print(f"Ungültiger Wert: {raw!r}")
                        continue
                else:
                    # Demo: Profil-basiert mit Rauschen
                    prof = self.profiles[self.current_profile]
                    if elapsed_min <= prof["times"][-1]:
                        base = float(np.interp(elapsed_min, prof["times"], prof["temps"]))
                    else:
                        base = prof["temps"][-1]
                    temp = base + random.uniform(-3.0, 3.0)

                # Daten puffern
                self.zeiten.append(elapsed_min)
                self.temperaturen.append(temp)

                # X-Achse bei Bedarf erweitern
                if elapsed_min >= self.max_x:
                    self.max_x += 10
                    self.set_x_ticks(self.max_x)

                # Live-Kurve aktualisieren
                self.line.set_data(self.zeiten, self.temperaturen)

                # Mittelwert der letzten Sekunde
                window = 1.0 / 60.0
                idxs = [
                    i for i, tm in enumerate(self.zeiten)
                    if elapsed_min - window <= tm <= elapsed_min
                ]
                if idxs:
                    m = sum(self.temperaturen[i] for i in idxs) / len(idxs)
                    self.mean_text.set_text(f"Mittelwert (1s): {m:.1f} °C")
                else:
                    self.mean_text.set_text("Mittelwert (1s): N/A")

                # Zeit-Text als mm:ss
                mins = int(elapsed_sec // 60)
                secs = int(elapsed_sec % 60)
                self.time_text.set_text(f"{mins:02d}:{secs:02d}")

                plt.pause(0.1)

        except KeyboardInterrupt:
            if self.ser is not None:
                self.ser.close()
            print("Beendet")

def main():
    # === 1) Argumente einlesen ===
    parser = argparse.ArgumentParser(
        description="Live-Röstkurve mit Referenzprofil und Demo-Modus."
    )
    parser.add_argument(
        "-p", "--profile",
        choices=["a", "ou", "kr", "s", "mm", "nsr", "bs", "brm", "tr", "cpe"],
        default="nsr",
        help=(
            "Referenzprofil:\n"
            "  a   = Alle\n"
            "  s   = Sidamo\n"
            "  mm  = Monsooned Malabar\n"
            "  nsr = Nicaragua San Ramon\n"
            "  bs  = Brasilien Santos\n"
            "  brm = Brasilien Rio Minas\n"
            "  ou  = Orang Utan\n"
            "  cpe = Cerro Prieto Estate\n"
            "  kr  = Kapi Robusta\n"
            "  tr  = Tanzania Robusta\n"
        )
    )
    parser.add_argument(
        "--port", default="/dev/ttyACM0",
        help="Serieller Port (Default /dev/ttyACM0)"
    )
    parser.add_argument(
        "--baud", type=int, default=115200,
        help="Baudrate (Default 115200)"
    )
    args = parser.parse_args()

    # === 2) Referenzprofildaten ===
    profiles = {
        "nsr": {
            "longname": "Nicaragua San Ramon",
            "times": [0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5,19],
            "temps": [195,86,70,75,83,90,98,104,110,116,121,125,130,133,138,142,146,150,154,158,162,166,169,173,176,179,182,185,187,190,192,193,195,197,199,201,204,207,208]
        },
        "bs": {
            "longname": "Brasilien Santos",
            "times": [0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5],
            "temps": [195,86,71,75,84,92,99,105,111,117,122,127,132,136,141,145,149,153,157,161,165,168,171,174,177,180,183,186,189,191,193,195,197,199,201,204,207,210]
        },
        "brm": {
            "longname": "Brasilien Rio Minas",
            "times": [0.0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.5,9.0,9.5,10.0,10.5,11.0,11.5,12.0,12.5,13.0,13.5,14.0,14.5,15.0,15.5,15.8],
            "temps": [213,91,70,74,85,96,106,116,125,133,140,146,151,156,160,163,170,173,177,180,184,187,191,195,199,203,207,210,214,218,222,225]
        },
        "mm": {
            "longname": "Monsooned Malabar",
            "times": [0.0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0,10.5,11.0,11.5,12.0,12.5,13.0,13.5,14.0,14.5,15.0,15.5],
            "temps": [213,90,70,74,82,93,103,113,121,129,138,142,148,153,157,160,164,167,170,174,177,180,183,186,190,194,198,201,204,206,209,212]
        },
        "s": {
            "longname": "Sidamo",
            "times": [0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.1],
            "temps": [195,86,69,74,82,90,98,105,112,119,125,130,136,141,146,151,155,160,164,169,173,178,182,186,190,194,196,197,198,200,203,204]
        },        "kr": {
            "longname": "Kapi Robusta",
            "times": [0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5,19,19.5],
            "temps": [195,86,70,75,83,90,98,105,111,117,122,127,132,136,140,144,148,152,155,159,163,167,171,174,176,179,182,185,188,190,192,194,197,199,201,204,207,210,213,214]
        },
        "ou": {
            "longname": "Orang Utan",
            "times": [0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5],
            "temps": [195,82,70,76,85,94,102,109,116,122,127,132,137,142,146,150,155,159,163,167,171,175,179,182,186,189,193,197,199,201,203,204]
        },
        "cpe": {
            "longname": "Cerro Prieto Estate",
            "times": [0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.5,9.0,9.5,10.0,10.5,11.0,11.5,12.0,12.5,13.0,13.5,14.0,14.5,15.0,15.5,15.9],
            "temps": [213,91,70,74,85,96,106,116,125,133,140,146,151,156,160,163,170,173,177,180,184,187,191,195,199,203,207,210,214,218,222,225]
        },
        "tr": {
            "longname": "Tanzania Robusta",
            "times": [0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17],
            "temps": [195,88,72,76,85,93,100,107,114,119,125,130,135,140,144,148,152,156,160,164,168,173,176,179,183,186,189,193,196,199,201,204,206,208,212]
        },
    }

    # === 3) Serielle Schnittstelle öffnen, sonst Demo-Modus ===
    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
    except (serial.SerialException, OSError):
        print("Kein serielles Gerät gefunden – starte Demo-Modus.")
        ser = None

    # === 4) Plot starten ===
    plotter = LiveRoastPlot(ser, profiles, args.profile)
    plt.ion()
    plotter.run()

if __name__ == "__main__":
    main()
