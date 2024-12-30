import argparse
import serial
import time
import matplotlib.pyplot as plt

def main():
    # === 1) ARGUMENTE EINLESEN ===
    parser = argparse.ArgumentParser(description="Zeige Live-Röstkurve und Referenzprofil.")
    parser.add_argument("-p", "--profile",
                        choices=["a", "ou", "kr", "s", "mm", "nsr", "bs", "brm", "tr", "cpe"], 
                        default="nsr",
                        help=(
                            "Welches Referenzprofil verwenden?\n"
                            "  a  = Alle Profile übereinander\n"
                            "  s  = Sidamo\n"
                            "  mm = Monsooned Malabar\n"
                            "  nsr= Nicaragua San Ramon\n"
                            "  bs = Brasilien Santos\n"
                            "  brm= Brasilien Rio Minas\n"
                            "  ou = Orang Utan\n"
                            "  cpe= Cerro Prieto Estate\n"
                            "  kr = Kapi Robusta\n"
                            "  tr= Tanzanina Robusta\n"
                            
                        ))
    parser.add_argument("--port", default="/dev/ttyUSB0",
                        help="Serieller Port (Default /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=115200,
                        help="Baudrate (Default 115200)")
    args = parser.parse_args()

    # === 2) REFERENZPROFILDATEN VORDEFINIEREN ===
    profiles = {
        "nsr": {
            "longname": "Kapi Robusta",
            "times": [
                0,  0.5,  1,  1.5,  2,  2.5,  3,  3.5,  4,  4.5,
                5,  5.5,  6,  6.5,  7,  7.5,  8,  8.5,  9,  9.5,
                10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5,
                15, 15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19
            ],
            "temps": [
                195, 86, 70, 75, 83, 90, 98, 104, 110, 116,
                121, 125, 130,133,138,142,146,150,154,158,
                162,166,169,173,176,179,182,185,187,190,
                192,193,195,197,199,201,204,207,208
            ]
        },
        "bs": {
            "longname": "Brasilien Santos",
            "times": [
                0,    0.5,  1,    1.5,  2,    2.5,  3,    3.5,  4,    4.5,
                5,    5.5,  6,    6.5,  7,    7.5,  8,    8.5,  9,    9.5,
                10,   10.5, 11,   11.5, 12,   12.5, 13,   13.5, 14,   14.5,
                15,   15.5, 16,   16.5, 17,   17.5, 18,   18.5
            ],
            "temps": [
                195,  86,   71,   75,   84,   92,   99,   105,  111,  117,
                122,  127,  132,  136,  141,  145,  149,  153,  157,  161,
                165,  168,  171,  174,  177,  180,  183,  186,  189,  191,
                193,  195,  197,  199,  201,  204,  207,  210
            ]
        },
        "brm": {
            "longname": "Brasilien Rio Minas",
            "times": [
                0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5,
                5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.5, 9.0, 9.5, 10.0,
                10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0,
                15.5, 15.8
            ],
            "temps": [
                213,  91,  70,  74,  85,  96, 106, 116, 125, 133,
                140, 146, 151, 156, 160, 163, 170, 173, 177, 180,
                184, 187, 191, 195, 199, 203, 207, 210, 214, 218,
                222, 225
            ]
        },
        "mm": {
            "longname": "Monsooned Malabar",
            "times": [
                0.0,  0.5,  1.0,  1.5,  2.0,  2.5,  3.0,  3.5,  4.0,  4.5,
                5.0,  5.5,  6.0,  6.5,  7.0,  7.5,  8.0,  8.5,  9.0,  9.5,
                10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5,
                15.0, 15.5
            ],
            "temps": [
                213,  90,  70,  74,  82,  93, 103, 113, 121, 129,
                138, 142, 148, 153, 157, 160, 164, 167, 170, 174,
                177, 180, 183, 186, 190, 194, 198, 201, 204, 206,
                209, 212
            ]
        },
        "s": {
            "longname": "Sidamo",
            "times": [
                0,    0.5,  1,    1.5,  2,    2.5,  3,    3.5,  4,    4.5,
                5,    5.5,  6,    6.5,  7,    7.5,  8,    8.5,  9,    9.5,
                10,   10.5, 11,   11.5, 12,   12.5, 13,   13.5, 14,   14.5,
                15,   15.1
            ],
            "temps": [
                195,  86,  69,  74,  82,  90,  98, 105, 112, 119,
                125, 130, 136, 141, 146, 151, 155, 160, 164, 169,
                173, 178, 182, 186, 190, 194, 196, 197, 198, 200,
                203, 204
            ]
        },
        "kr": {
            "longname": "Kapi Robusta",
            "times": [
                0,    0.5,  1,    1.5,  2,    2.5,  3,    3.5,  4,    4.5,
                5,    5.5,  6,    6.5,  7,    7.5,  8,    8.5,  9,    9.5,
                10,   10.5, 11,   11.5, 12,   12.5, 13,   13.5, 14,   14.5,
                15,   15.5, 16,   16.5, 17,   17.5, 18,   18.5, 19,   19.5
            ],
            "temps": [
                195,  86,  70,  75,  83,  90,  98, 105, 111, 117,
                122, 127, 132, 136, 140, 144, 148, 152, 155, 159,
                163, 167, 171, 174, 176, 179, 182, 185, 188, 190,
                192, 194, 197, 199, 201, 204, 207, 210, 213, 214
            ]
        },
        "ou": {
            "longname": "Orang Utan",
            "times": [
                0,   0.5,  1,   1.5,  2,   2.5,  3,   3.5,  4,   4.5,
                5,   5.5,  6,   6.5,  7,   7.5,  8,   8.5,  9,   9.5,
                10, 10.5, 11,  11.5, 12,  12.5, 13,  13.5, 14,  14.5,
                15, 15.5
            ],
            "temps": [
                195, 82,  70,  76,  85,  94,  102, 109, 116, 122,
                127, 132, 137, 142, 146, 150, 155, 159, 163, 167,
                171, 175, 179, 182, 186, 189, 193, 197, 199, 201,
                203, 204
            ]
        },
        "cpe": {
            "longname": "Cerro Prieto Estate",
            "times": [
                0,    0.5,  1.0,  1.5,  2.0,  2.5,  3.0,  3.5,  4.0,  4.5,
                5.0,  5.5,  6.0,  6.5,  7.0,  7.5,  8.5,  9.0,  9.5, 10.0,
                10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0,
                15.5, 15.9
            ],
            "temps": [
                213,  91,   70,  74,   85,   96,   106, 116, 125, 133,
                140,  146,  151, 156,  160,  163,  170, 173, 177, 180,
                184,  187,  191, 195,  199,  203,  207, 210, 214, 218,
                222,  225
            ]
        },
        "tr": {
            "longname": "Tanzania Robusta",
            "times": [
                0,   0.5,  1,   1.5,  2,   2.5,  3,   3.5,  4,   4.5,
                5,   5.5,  6,   6.5,  7,   7.5,  8,   8.5,  9,   9.5,
                10, 10.5, 11,  11.5, 12,  12.5, 13,  13.5, 14,  14.5,
                15, 15.5, 16,  16.5, 17
            ],
            "temps": [
                195, 88,  72,  76,  85,  93, 100, 107, 114, 119,
                125, 130, 135, 140, 144, 148, 152, 156, 160, 164,
                168, 173, 176, 179, 183, 186, 189, 193, 196, 199,
                201, 204, 206, 208, 212
            ]
        }
    }

    chosen_profile = args.profile

    # === 3) SERIELLE SCHNITTSTELLE ===
    ser = serial.Serial(args.port, args.baud, timeout=1)

    # === 4) INITIALISIERUNG PLOT ===
    start_time = time.time()
    zeiten = []
    temperaturen = []

    plt.ion()
    fig, ax = plt.subplots()

    # -------------------------------------------------------------
    # WENN -p a => ALLE PROFILE
    # -------------------------------------------------------------
    if chosen_profile == "a":
        for prof_key, prof_data in profiles.items():
            long_name = prof_data.get("longname", prof_key)
            ax.plot(
                prof_data["times"],
                prof_data["temps"],
                '--',
                label=long_name
            )
    else:
        # NUR DAS AUSGEWÄHLTE PROFIL
        prof_data = profiles[chosen_profile]
        long_name = prof_data.get("longname", chosen_profile)
        ax.plot(
            prof_data["times"],
            prof_data["temps"],
            'g--',
            label=long_name
        )

    # LIVE-KURVE (rot)
    line, = ax.plot([], [], 'r-', label='Live-Daten')

    max_x = 20
    ax.set_xlim(0, max_x)
    ax.set_ylim(0, 250)
    ax.set_xlabel('Zeit (min)')
    ax.set_ylabel('Temperatur (°C)')

    # Legende
    leg = ax.legend(loc='upper left')

    # Gitter
    ax.set_yticks(range(0, 251, 10))
    ax.grid(which='major', axis='both', linestyle='--', alpha=0.7)

    # X-Achse: Jede Minute ein Tick
    def set_x_ticks(xmax):
        ax.set_xlim(0, xmax)
        ax.set_xticks(range(0, xmax + 1, 1))

    set_x_ticks(max_x)

    # TEXT-Element rechts neben der Legende platzieren
    plt.draw()  # Legendengröße bekannt machen
    legend_bbox = leg.get_window_extent()
    inv = ax.transAxes.inverted()
    legend_bbox_axes = legend_bbox.transformed(inv)
    lx0, ly0, lx1, ly1 = legend_bbox_axes.extents
    text_x = lx1 + 0.02
    text_y = ly1

    #mean_text = ax.text(text_x, text_y, "", transform=ax.transAxes, va='top', ha='left')
    mean_text = ax.text(
    text_x, text_y, "", 
    transform=ax.transAxes, 
    fontsize=14,  # Größere Schrift (z. B. 14 statt Standard ~10)
    fontweight='bold',  # Fett
    color='blue',       # Farbe (optional)
    va='top', 
    ha='left'
)

    # === 5) HAUPTSCHLEIFE (LIVE-DATEN) ===
    try:
        while True:
            data = ser.readline().decode('utf-8').strip()
            if data:
                try:
                    temperatur = float(data)-3.7

                    aktuelle_zeit_sek = time.time() - start_time
                    aktuelle_zeit_min = aktuelle_zeit_sek / 60.0

                    zeiten.append(aktuelle_zeit_min)
                    temperaturen.append(temperatur)

                    if aktuelle_zeit_min >= max_x:
                        max_x += 10
                        set_x_ticks(max_x)

                    # Live-Kurve updaten
                    line.set_xdata(zeiten)
                    line.set_ydata(temperaturen)

                    # Mittelwert der letzten 1 Sekunde
                    sekunden_fenster = 1.0 / 60.0
                    min_grenze = aktuelle_zeit_min - sekunden_fenster

                    relevant_indices = [
                        i for i in range(len(zeiten))
                        if min_grenze <= zeiten[i] <= aktuelle_zeit_min
                    ]

                    if relevant_indices:
                        mean_temp = sum(temperaturen[i] for i in relevant_indices) / len(relevant_indices)
                        mean_text.set_text(f"Mittelwert (1s): {mean_temp:.1f} °C")
                    else:
                        mean_text.set_text("Mittelwert (1s): N/A")

                    plt.draw()
                    plt.pause(0.1)

                except ValueError:
                    print(f"Ungültiger Wert empfangen: {data}")

    except KeyboardInterrupt:
        ser.close()
        print("Beendet")


if __name__ == "__main__":
    main()
