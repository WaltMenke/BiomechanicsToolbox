import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.signal import find_peaks
from ToolboxFunctions import batch_reshape
from itertools import cycle, islice


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = (screen_width - width) // 2
    y_coordinate = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


def exit_window():
    result = messagebox.askyesno("Exit", "Do you really want to exit?")
    if result:
        root.destroy()
    pass


def restart_events():
    pass


def save_events():  # Remember to pass the output directory here to auto save, also check if file is already there
    pass


def create_figure():
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.get_tk_widget().grid(row=0, column=0, columnspan=1, rowspan=20, sticky="w")
    # canvas.draw_idle
    return fig, ax, canvas


def create_treeview(parent, row, column, rowspan, heading_text, columns, column_widths):
    if column == 1:
        max_label = ttk.Label(root, text="Maxima", font=("Helvetica", 10))
        max_label.grid(row=10, column=1, columnspan=1)
    else:
        min_label = ttk.Label(root, text="Minima", font=("Helvetica", 10))
        min_label.grid(row=10, column=2, columnspan=1)

    tree = ttk.Treeview(parent)
    tree.grid(row=row, column=column, rowspan=rowspan, padx=10, sticky="n")
    tree["columns"] = columns

    tree.heading("#0", text=heading_text, anchor="w")

    for col, width in zip(columns, column_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, minwidth=width, anchor="center")
    tree.column("#0", width=column_widths[0])
    tree["height"] = 4
    return tree


def treeview_contents(tree, time_series):
    tree.delete(*tree.get_children())
    max_idx_sorted, min_idx_sorted, _, _ = find_prominent(time_series)
    for i, idx in (
        enumerate(max_idx_sorted) if tree == tree_max else enumerate(min_idx_sorted)
    ):
        tree.insert(
            "",
            "end",
            text=f"{i + 1}",
            values=(idx, np.round(time_series[idx], 3)),
        )


def update_tree(tree, idx_list, time_series):
    tree.delete(*tree.get_children())
    for i, idx in enumerate(idx_list):
        if np.isnan(idx) or idx < 0 or idx >= len(time_series):
            value = 0
        else:
            value = time_series[int(idx)]

        tree.insert(
            "",
            "end",
            text=f"{i + 1}",
            values=(idx, np.round(value, 3)),
        )


def create_button_style(style_name, foreground, background):
    style = ttk.Style()
    style.configure(
        style_name,
        font=("Helvetica", 10),
        foreground=foreground,
        background=background,
        bordercolor=0,
    )
    style.map(
        style_name,
        foreground=[("pressed", foreground), ("active", foreground)],
        background=[("pressed", "gray"), ("active", background)],
    )
    return style_name


def create_button(
    parent,
    text,
    command,
    row=0,
    column=0,
    sticky="",
    padx=5,
    pady=5,
    columnspan=1,
    rowspan=1,
    style=None,
    bgcolor=None,
):
    button = ttk.Button(parent, text=text, command=command, style=style, cursor="hand2")
    button.grid(
        row=row,
        column=column,
        sticky=sticky,
        padx=padx,
        pady=pady,
        columnspan=columnspan,
        rowspan=rowspan,
    )
    if bgcolor:
        button_style = ttk.Style()
        button_style.configure(style)
    return button


def create_button_group(btn_specs, parent):
    for idx in range(3):  # Placing Max and Min buttons
        for label, update_func, sticky, style in btn_specs:
            create_button(
                parent,
                f"{label} {idx + 1}",
                # lambda: update_func(idx, max_idx, min_idx, ax, tree_max, tree_min),
                lambda: update_func(),
                row=idx + 1,
                column=1 if label == "Max" else 2,
                sticky=sticky,
                style=style,
            )


def place_button_group(parent, row, column, rowspan, label_text, btn_specs):
    frame = ttk.Frame(parent)
    frame.grid(row=row, column=column, rowspan=rowspan, padx=10, pady=10, sticky="n")

    separator = ttk.Separator(frame, orient=tk.HORIZONTAL)
    separator.grid(row=0, column=1, columnspan=2, sticky="ew")

    label = ttk.Label(frame, text=label_text, font=("Helvetica", 10))
    label.grid(row=0, column=1, padx=15, columnspan=2)

    create_button_group(btn_specs, frame)


def place_general_buttons(parent, button_specs, buttons):
    for text, command, row, column, style in button_specs:
        button = create_button(
            parent,
            text,
            command,
            row=row,
            column=column,
            sticky="",
            padx=5,
            pady=5,
            style=style,
        )
        buttons.append(button)


def find_prominent(data, prominence=0.5, distance=12):
    maxes = []
    max_idx, _ = find_peaks(data, prominence=prominence, distance=distance)
    max_idx_sorted = sorted(max_idx[:3])
    maxes = data[max_idx_sorted]

    mins = []
    inverted_data = [-x for x in data]
    min_idx, _ = find_peaks(inverted_data, prominence=prominence, distance=distance)
    min_idx_sorted = sorted(min_idx[:3])
    mins = data[min_idx_sorted]

    return max_idx_sorted, min_idx_sorted, maxes, mins


def scale_plot(ax):
    x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]

    padding_percentage = (
        0.05  # Adjust this value based on the percentage of padding you want
    )

    ax.set_xlim(
        ax.get_xlim()[0] - padding_percentage * x_range,
        ax.get_xlim()[1] + padding_percentage * x_range,
    )
    ax.set_ylim(
        ax.get_ylim()[0] - padding_percentage * y_range,
        ax.get_ylim()[1] + padding_percentage * y_range,
    )


def plot_time_series(ax, data, var_list, plot_subtitles):
    global plot_idx
    ax.plot(data, color="black", linewidth=1, zorder=1)
    ax.set_title(f"{var_list[plot_idx]}\n{plot_subtitles[plot_idx]}")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Value")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    scale_plot(ax)


def plot_events(max_idx, min_idx, time_series):
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    offset_percentage = 0.025
    offset = offset_percentage * y_range
    if len(max_idx) > 0 and not np.isnan(max_idx[0]):
        idx = int(max_idx[0])
        if 0 <= idx < len(time_series):
            ax.scatter(
                idx,
                time_series[idx] + offset,
                color="dodgerblue",
                marker="v",
                s=70,
                zorder=2,
            )

    if len(min_idx) > 0 and not np.isnan(min_idx[0]):
        idx = int(min_idx[0])
        if 0 <= idx < len(time_series):
            ax.scatter(
                idx,
                time_series[idx] - offset,
                color="firebrick",
                marker="^",
                s=70,
                zorder=2,
            )


def set_plot(ax, time_series):
    global plot_idx
    max_idx, min_idx, _, _ = find_prominent(time_series)
    plot_time_series(ax, time_series, var_list, plot_subtitles)
    plot_events(max_idx, min_idx, time_series)


def nan_sort(elem):
    if np.isnan(elem):
        return float(
            "inf"
        )  # Treat np.nan as greater than any other value to place at end
    return elem


def update_max():
    pass


def update_min():
    pass


def clear_max(button_idx, max_idx, min_idx, ax, tree_max, _):
    print(f"Clear Max {button_idx+1} Pressed")
    max_idx[button_idx] = np.nan
    ax.clear()
    plot_time_series(ax, time_series, var_list, plot_subtitles)
    new_max_idx = sorted(max_idx, key=nan_sort)
    plot_events(new_max_idx, min_idx)
    update_tree(tree_max, new_max_idx, time_series)
    canvas.draw_idle()


def clear_min():
    pass


def reset_current():
    pass


def iterate_plot(subsection_time_series, ax):
    global plot_idx
    time_series = subsection_time_series[:, plot_idx]
    max_idx, min_idx, _, _ = find_prominent(time_series)
    ax.clear()
    update_tree(tree_max, max_idx, time_series)
    update_tree(tree_min, min_idx, time_series)
    set_plot(ax, time_series)
    ax.relim()
    ax.autoscale_view()
    canvas.draw()


def next_plot(subsection_time_series, ax):
    global plot_idx
    plot_idx += 1
    iterate_plot(subsection_time_series, ax)


def previous_plot(subsection_time_series, ax):
    global plot_idx
    plot_idx -= 1
    iterate_plot(subsection_time_series, ax)


root = ttk.Window()
center_window(root, 1000, 525)

subject = 1
condition = 1

plots_file = "L:\Zhang\WaltMenke\Dissertation\Pilot\PythonIntegration\R_S1.txt"
full_series, raw_var_list, _, components = batch_reshape(
    plots_file
)  # imports 3d matrix
file_idx = 0  # user specified file number (to navigate slice in Batch output)
subsection_time_series_raw = full_series[:, :, file_idx]
trials = int(subsection_time_series_raw.shape[1] / len(raw_var_list))
plot_idx = 0

adjusted_var_list = raw_var_list[0 :: len(components)]  # removes duplicates
var_list = []
for (
    raw_var
) in adjusted_var_list:  # appends X, Y, Z to each variable according to trial number
    for _ in range(5):
        var_list.append(f"{raw_var} X")
    for _ in range(5):
        var_list.append(f"{raw_var} Y")
    for _ in range(5):
        var_list.append(f"{raw_var} Z")

subsection_time_series_adjusted = np.reshape(
    subsection_time_series_raw,
    (subsection_time_series_raw.shape[0], len(raw_var_list), trials),
    order="F",
)
subsection_time_series = np.reshape(
    np.transpose(subsection_time_series_adjusted, (0, 2, 1)),
    (subsection_time_series_adjusted.shape[0], -1),
    order="F",
)

time_series = subsection_time_series[:, plot_idx]

raw_plot_subtitles = []
for trial in range(trials):
    raw_plot_subtitles.append(f"S{subject} C{condition} T{trial+1}")
plot_subtitles = list(
    islice(cycle(raw_plot_subtitles), subsection_time_series.shape[1])
)
print(f"Plot Subtitles Size: {len(plot_subtitles)}")

max_btn_style = create_button_style("max.TButton", "white", "dodgerblue")
min_btn_style = create_button_style("min.TButton", "white", "firebrick")
navigate_btn_style = create_button_style("navigate.TButton", "white", "slategray")
save_btn_style = create_button_style("save.TButton", "white", "#FF8200")

replace_btn_specs = [
    ("Max", update_max, "e", "max.TButton"),
    ("Min", update_min, "w", "min.TButton"),
]
clear_btn_specs = [
    ("Max", clear_max, "e", "max.TButton"),
    ("Min", clear_min, "w", "min.TButton"),
]
general_btn_specs = [
    (
        "Reset Plot",
        lambda: reset_current(time_series, ax),
        17,
        1,
        "navigate.TButton",
    ),
    (
        "Next Plot",
        lambda: next_plot(subsection_time_series, ax),
        1,
        2,
        "navigate.TButton",
    ),
    (
        "Previous Plot",
        lambda: previous_plot(subsection_time_series, ax),
        1,
        1,
        "navigate.TButton",
    ),
    ("Save All Events", lambda: save_events(), 17, 2, "save.TButton"),
]

# Calls to populate the window initially
fig, ax, canvas = create_figure()
set_plot(ax, time_series)
general_buttons = []
place_general_buttons(root, general_btn_specs, general_buttons)
place_button_group(
    root, row=2, column=1, rowspan=25, label_text="Replace", btn_specs=replace_btn_specs
)
place_button_group(
    root, row=2, column=2, rowspan=25, label_text="Clear", btn_specs=clear_btn_specs
)
tree_max = create_treeview(root, 11, 1, 6, "Event", ("Frame", "Value"), (55, 70))
treeview_contents(tree_max, time_series)
tree_min = create_treeview(root, 11, 2, 6, "Event", ("Frame", "Value"), (55, 70))
treeview_contents(tree_min, time_series)
#################

file_menu_items = {
    "Save": save_events,
    "Restart": restart_events,
    "Exit": exit_window,
}

menubar = ttk.Menu(master=root)
fileMenu = ttk.Menu(menubar)
for item, command in file_menu_items.items():
    fileMenu.add_command(label=item, command=command)
menubar.add_cascade(label="Options", menu=fileMenu)
root.config(menu=menubar)
root.iconbitmap("BT_Icon.ico")
root.title("Biomechanics Toolbox - Event Picking")

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=0)

root.mainloop()
