import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.signal import find_peaks


def exit_window():
    result = messagebox.askyesno("Exit", "Do you really want to exit?")
    if result:
        root.destroy()
    pass


def restart_events():
    pass


def save_events():  # Remember to pass the output directory here to auto save, also check if file is already there
    print("Saving events...")


def center_window(window, width_percent, height_percent):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    width = int(screen_width * width_percent / 100)
    height = int(screen_height * height_percent / 100)
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.minsize(width, height)
    window.maxsize(width, height)


def create_figure():
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.get_tk_widget().grid(row=0, column=0, columnspan=1, rowspan=20, sticky="w")
    # canvas.draw_idle
    return fig, ax, canvas


def find_prominent(data, prominence=0.7, distance=15):
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


def plot_time_series(ax, data):
    ax.plot(data, color="black", linewidth=1, zorder=1)
    ax.set_title("Random Time Series")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Value")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)


def plot_events(max_idx, min_idx):
    offset = 0.125
    for idx in max_idx:
        if not np.isnan(idx):
            ax.scatter(
                idx,
                random_time_series[int(idx)] + offset,
                color="dodgerblue",
                marker="v",
                s=70,
                zorder=2,
            )

    for idx in min_idx:
        if not np.isnan(idx):
            ax.scatter(
                idx,
                random_time_series[int(idx)] - offset,
                color="firebrick",
                marker="^",
                s=70,
                zorder=2,
            )


def nan_sort(elem):
    if np.isnan(elem):
        return float("inf")  # Treat np.nan as greater than any other value
    return elem


def clear_max(button_idx, max_idx, min_idx, ax, tree_max, _):
    print(f"Max {button_idx+1} Pressed")
    max_idx[button_idx] = np.nan
    ax.clear()
    plot_time_series(ax, random_time_series)
    new_max_idx = sorted(max_idx, key=nan_sort)
    plot_events(new_max_idx, min_idx)
    update_tree(tree_max, new_max_idx, random_time_series)
    canvas.draw_idle()


def update_max(button_idx, max_idx, min_idx, ax, tree_max, _):
    def update_max_point(event):
        x_click = int(event.xdata)
        search_range = range(
            max(0, x_click - 12), min(len(random_time_series), x_click + 13)
        )
        local_maxima = max(search_range, key=lambda i: random_time_series[i])
        max_idx[button_idx] = local_maxima

        ax.clear()
        plot_time_series(ax, random_time_series)
        plot_events(max_idx, min_idx)
        canvas.draw_idle()
        canvas.mpl_disconnect(cid_click)

        new_max_idx = sorted(max_idx, key=nan_sort)
        update_tree(tree_max, new_max_idx, random_time_series)
        print(f"New Max Locations: {new_max_idx}")
        return new_max_idx, min_idx

    print(f"Max {button_idx+1} Pressed (idx: {button_idx})")
    max_idx[button_idx] = np.nan
    ax.clear()
    plot_time_series(ax, random_time_series)
    new_max_idx = sorted(max_idx, key=nan_sort)
    plot_events(new_max_idx, min_idx)
    update_tree(tree_max, new_max_idx, random_time_series)
    canvas.draw_idle()
    canvas.mpl_connect("button_press_event", update_max_point)
    cid_click = canvas.mpl_connect("button_press_event", update_max_point)


def clear_min(button_idx, max_idx, min_idx, ax, _, tree_min):
    print(f"Min {button_idx+1} Pressed")
    min_idx[button_idx] = np.nan
    ax.clear()
    plot_time_series(ax, random_time_series)
    new_min_idx = sorted(min_idx, key=nan_sort)
    plot_events(max_idx, new_min_idx)
    update_tree(tree_min, new_min_idx, random_time_series)
    canvas.draw_idle()


def update_min(button_idx, max_idx, min_idx, ax, _, tree_min):
    def update_min_point(event):
        x_click = int(event.xdata)
        search_range = range(
            max(0, x_click - 12), min(len(random_time_series), x_click + 13)
        )
        inverted_data = [-x for x in random_time_series]
        local_minima = max(search_range, key=lambda i: inverted_data[i])
        min_idx[button_idx] = local_minima

        ax.clear()
        plot_time_series(ax, random_time_series)
        plot_events(max_idx, min_idx)
        canvas.draw_idle()
        canvas.mpl_disconnect(cid_click)
        new_min_idx = sorted(min_idx, key=nan_sort)
        update_tree(tree_min, new_min_idx, random_time_series)
        print(f"New Min Locations: {new_min_idx}")
        return max_idx, new_min_idx

    print(f"Min {button_idx+1} Pressed")
    min_idx[button_idx] = np.nan
    ax.clear()
    plot_time_series(ax, random_time_series)
    new_min_idx = sorted(min_idx, key=nan_sort)
    plot_events(max_idx, new_min_idx)
    update_tree(tree_min, new_min_idx, random_time_series)
    canvas.draw_idle()
    cid_click = canvas.mpl_connect("button_press_event", update_min_point)


def reset_current(time_series, ax):
    ax.cla()
    max_idx, min_idx, _, _ = find_prominent(time_series)
    plot_time_series(ax, time_series)
    plot_events(max_idx, min_idx)
    update_tree(tree_max, max_idx, time_series)
    update_tree(tree_min, min_idx, time_series)
    set_button_frame(
        root,
        row=2,
        column=1,
        rowspan=25,
        label_text="Replace",
        btn_specs=replace_btn_specs,
    )
    set_button_frame(
        root, row=2, column=2, rowspan=25, label_text="Clear", btn_specs=clear_btn_specs
    )

    canvas.draw_idle()
    print("Resetting...")


def place_button(
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


def create_update_button(
    parent, label, update_func, idx, row, column, sticky, style=None, bgcolor=None
):
    button = place_button(
        parent,
        label,
        lambda: update_func(idx, max_idx, min_idx, ax, tree_max, tree_min),
        row=row,
        column=column,
        sticky=sticky,
        style=style,
        bgcolor=bgcolor,
    )
    return button


def place_btn_group(
    btn_specs,
    parent,
):
    for idx in range(0, 3):  # Placing Max and Min buttons
        for label, update_func, sticky, style in btn_specs:
            create_update_button(
                parent,
                f"{label} {idx+1}",
                update_func,
                idx,
                row=idx + 1,
                column=1 if label == "Max" else 2,
                sticky=sticky,
                style=style,
            )


def create_treeview(parent, row, column, rowspan, heading_text, columns, column_widths):
    tree = ttk.Treeview(parent)
    tree.grid(row=row, column=column, rowspan=rowspan, padx=10, sticky="n")
    tree["columns"] = columns

    tree.heading("#0", text=heading_text, anchor="w")

    for col, width in zip(columns, column_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, minwidth=width, anchor="center")
    tree.column("#0", width=column_widths[0])
    return tree


def update_tree(tree, idx_list, random_time_series):
    for item in tree.get_children():
        tree.delete(item)

    for i, idx in enumerate(idx_list):
        if np.isnan(idx) or idx < 0 or idx >= len(random_time_series):
            value = 0
        else:
            value = random_time_series[int(idx)]

        tree.insert(
            "",
            "end",
            text=f"{i + 1}",
            values=(idx, np.round(value, 3)),
        )


def configure_button_style(style_name, foreground, background):
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


def set_button_frame(parent, row, column, rowspan, label_text, btn_specs):
    frame = ttk.Frame(parent)
    frame.grid(row=row, column=column, rowspan=rowspan, padx=10, pady=10, sticky="n")

    separator = ttk.Separator(frame, orient=tk.HORIZONTAL)
    separator.grid(row=0, column=1, columnspan=2, sticky="ew")

    label = ttk.Label(frame, text=label_text, font=("Helvetica", 10))
    label.grid(row=0, column=1, padx=15, columnspan=2)

    place_btn_group(btn_specs, frame)


def next_plot():
    pass


def previous_plot():
    pass


def save_events():
    messagebox.askyesno(
        "Save",
        "Are you sure you want to save all events?",
    )


root = ttk.Window()
center_window(root, 40, 40)

np.random.seed(42)
t = np.linspace(0, 2 * np.pi, 200)
random_time_series = 1.5 * np.sin(2 * t) + 0.5 * np.cos(4 * t) - 1.0 * np.sin(6 * t)

fig, ax, canvas = create_figure()
max_idx, min_idx, maxes, mins = find_prominent(random_time_series)
print(
    f"Max Locations: {max_idx}\nMin Locations: {min_idx}\nMaxes: {maxes}\nMins: {mins}"
)
plot_time_series(ax, random_time_series)
plot_events(max_idx, min_idx)

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=0)


max_btn_style = configure_button_style("max.TButton", "white", "dodgerblue")
min_btn_style = configure_button_style("min.TButton", "white", "firebrick")
navigate_btn_style = configure_button_style("navigate.TButton", "white", "slategray")
save_btn_style = configure_button_style("save.TButton", "white", "#FF8200")

replace_btn_specs = [
    ("Max", update_max, "e", "max.TButton"),
    ("Min", update_min, "w", "min.TButton"),
]
set_button_frame(
    root, row=2, column=1, rowspan=25, label_text="Replace", btn_specs=replace_btn_specs
)

clear_btn_specs = [
    ("Max", clear_max, "e", "max.TButton"),
    ("Min", clear_min, "w", "min.TButton"),
]
set_button_frame(
    root, row=2, column=2, rowspan=25, label_text="Clear", btn_specs=clear_btn_specs
)

button_specs = [
    (
        "Reset Plot",
        lambda: reset_current(random_time_series, ax),
        17,
        1,
        "navigate.TButton",
    ),
    ("Next Plot", lambda: next_plot(random_time_series, ax), 1, 2, "navigate.TButton"),
    (
        "Previous Plot",
        lambda: previous_plot(random_time_series, ax),
        1,
        1,
        "navigate.TButton",
    ),
    ("Save All Events", lambda: save_events(), 17, 2, "save.TButton"),
]

buttons = []
for text, command, row, column, style in button_specs:
    button = place_button(
        root,
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


max_label = ttk.Label(root, text="Maxima", font=("Helvetica", 10))
max_label.grid(row=10, column=1, columnspan=1)
tree_max = create_treeview(root, 11, 1, 6, "Event", ("Frame", "Value"), (55, 70))
for i, idx in enumerate(max_idx):
    tree_max.insert(
        "",
        "end",
        text=f"{i + 1}",
        values=(idx, np.round(random_time_series[idx], 3)),
    )
tree_max["height"] = len(max_idx) + 1


min_label = ttk.Label(root, text="Minima", font=("Helvetica", 10))
min_label.grid(row=10, column=2, columnspan=1)
tree_min = create_treeview(root, 11, 2, 6, "Event", ("Frame", "Value"), (55, 70))
for i, idx in enumerate(min_idx):
    tree_min.insert(
        "",
        "end",
        text=f"{i + 1}",
        values=(idx, np.round(random_time_series[idx], 3)),
    )
tree_min["height"] = len(min_idx) + 1

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


root.mainloop()
