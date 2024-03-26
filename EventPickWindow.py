import os
import sys

import tkinter as tk
from tkinter import ttk, filedialog, PhotoImage, messagebox, simpledialog
import ttkbootstrap as ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.signal import find_peaks

from ToolboxFunctions import batch_reshape
from itertools import cycle, islice
import csv
from matplotlib.backend_bases import MouseButton

from functools import partial
import openpyxl


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = (screen_width - width) // 2
    y_coordinate = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


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


def create_manipulate_button(
    parent, label, update_func, idx, row, column, sticky, style=None, bgcolor=None
):
    button = create_button(
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


def place_manipulate_buttons(
    btn_specs,
    parent,
):
    for idx in range(0, 3):  # Placing Max and Min buttons
        for label, update_func, sticky, style in btn_specs:
            create_manipulate_button(
                parent,
                f"{label} {idx+1}",
                update_func,
                idx,
                row=idx + 1,
                column=1 if label == "Max" else 2,
                sticky=sticky,
                style=style,
            )


def set_button_frame(parent, row, column, rowspan, label_text, btn_specs):
    frame = ttk.Frame(parent)
    frame.grid(row=row, column=column, rowspan=rowspan, padx=10, pady=10, sticky="n")

    separator = ttk.Separator(frame, orient=tk.HORIZONTAL)
    separator.grid(row=0, column=1, columnspan=2, sticky="ew")

    label = ttk.Label(frame, text=label_text, font=("Helvetica", 10))
    label.grid(row=0, column=1, padx=15, columnspan=2)

    place_manipulate_buttons(btn_specs, frame)


def create_figure():
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=0, column=0, columnspan=1, rowspan=20, sticky="w")
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
    max_entries = min(3, len(max_idx_sorted))
    min_entries = min(3, len(min_idx_sorted))

    for i, idx in (
        enumerate(max_idx_sorted[:max_entries])
        if tree == tree_max
        else enumerate(min_idx_sorted[:min_entries])
    ):
        tree.insert(
            "",
            "end",
            text=f"{i + 1}",
            values=(idx, np.round(time_series[idx], 3)),
        )
    if tree == tree_max:
        remaining = 3 - max_entries
    else:
        remaining = 3 - min_entries
    for j in range(remaining):
        tree.insert(
            "",
            "end",
            text=f"{remaining + j}" if remaining != 1 else "3",
            values=(np.nan, 0),
        )


def update_tree(tree, idx_list, time_series):
    tree.delete(*tree.get_children())
    try:
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
        remaining = 3 - min(3, len(idx_list))
        if remaining >= 3:
            remaining = 3
            for j in range(remaining):
                tree.insert(
                    "",
                    "end",
                    text=f"{j+1}" if remaining != 1 else "3",
                    values=(np.nan, 0),
                )
        else:
            for j in range(remaining):
                tree.insert(
                    "",
                    "end",
                    text=f"{remaining + j}" if remaining != 1 else "3",
                    values=(np.nan, 0),
                )
    except UnboundLocalError:  # means there are no events by default
        for _ in range(3):
            tree.insert(
                "",
                "end",
                text="---",
                values=(np.nan, 0),
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

    padding_percentage = 0.1

    ax.set_xlim(
        ax.get_xlim()[0] - padding_percentage * x_range,
        ax.get_xlim()[1] + padding_percentage * x_range,
    )
    ax.set_ylim(
        ax.get_ylim()[0] - padding_percentage * y_range,
        ax.get_ylim()[1] + padding_percentage * y_range,
    )


def plot_time_series(ax, data, var_titles, plot_subtitles):
    global plot_idx
    ax.plot(data, color="black", linewidth=1, zorder=1)
    ax.set_title(f"{var_titles[plot_idx]}\n{plot_subtitles[plot_idx]}")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Value")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    scale_plot(ax)


def plot_events(max_idx, min_idx, time_series):
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    offset_percentage = 0.025
    offset = offset_percentage * y_range

    counter = 0
    if len(max_idx) > 0:
        for idx in max_idx:
            if not np.isnan(idx):
                idx = int(idx)
                if 0 <= idx < len(time_series):
                    counter += 1
                    ax.scatter(
                        idx,
                        time_series[idx] + offset,
                        color="dodgerblue",
                        marker="v",
                        s=70,
                        zorder=2,
                    )
                    ax.text(
                        idx,
                        time_series[idx] + (offset * 2),
                        f"{counter}",
                        ha="center",
                        va="bottom",
                        fontdict={"size": 12, "color": "dodgerblue"},
                    )
    counter = 0
    if len(min_idx) > 0:
        for idx in min_idx:
            if not np.isnan(idx):
                idx = int(idx)
                if 0 <= idx < len(time_series):
                    counter += 1
                    ax.scatter(
                        idx,
                        time_series[idx] - offset,
                        color="firebrick",
                        marker="^",
                        s=70,
                        zorder=2,
                    )
                    ax.text(
                        idx,
                        time_series[idx] - (offset * 2.2),
                        f"{counter}",
                        ha="center",
                        va="top",
                        fontdict={"size": 12, "color": "firebrick"},
                    )


def set_plot(ax, time_series):
    global plot_idx
    max_idx, min_idx, _, _ = find_prominent(time_series)
    plot_time_series(ax, time_series, var_titles, plot_subtitles)
    plot_events(max_idx, min_idx, time_series)

    return max_idx, min_idx


def nan_sort(elem):
    if np.isnan(elem):
        return float(
            "inf"
        )  # Treat np.nan as greater than any other value to place at end
    return elem


def update_max(button_idx, max_idx, min_idx, ax, tree_max, _):
    global plot_idx, plots_file, max_cid
    try:  # Passes error where max_cid doesn't exist on first code run
        fig.canvas.mpl_disconnect(max_cid)
    except NameError:
        pass
    clear_max(button_idx, max_idx, min_idx, ax, tree_max, _)

    def update_max_value(new_max):
        time_series = np.ravel(plots_file[:, plot_idx])
        max_idx, min_idx = get_current_idxs(plot_idx)

        max_idx[button_idx] = new_max
        new_max_idx = sorted(max_idx, key=nan_sort)
        ax.clear()

        plot_time_series(ax, time_series, var_titles, plot_subtitles)

        plot_events(new_max_idx, min_idx, time_series)
        update_tree(tree_max, new_max_idx, time_series)
        max_idx = new_max_idx
        update_max_matrices(
            max_idx,
            time_series,
            plot_idx,
            all_maxidx_matrix,
            all_maxval_matrix,
            all_maxper_matrix,
            trials,
        )
        canvas.draw_idle()

    def set_max_event(event):
        if event.inaxes and event.button == MouseButton.LEFT:
            time_series = np.ravel(plots_file[:, plot_idx])
            new_event = round(event.xdata)
            possible_indices = np.arange(
                new_event - find_tolerance, new_event + find_tolerance
            )
            possible_indices = possible_indices[
                (possible_indices >= 0) & (possible_indices < len(time_series))
            ]
            try:
                desired_index_within_range = np.argmin(time_series[possible_indices])
            except ValueError:
                messagebox.showwarning(
                    "Warning", "You clicked out of the graph bounds. Please try again."
                )
                return
            desired_index_within_range = np.argmax(time_series[possible_indices])
            desired_index = possible_indices[desired_index_within_range]
            update_max_value(desired_index)
            fig.canvas.mpl_disconnect(max_cid)

    max_cid = fig.canvas.mpl_connect("button_press_event", set_max_event)


def update_min(button_idx, max_idx, min_idx, ax, _, tree_min):
    global plot_idx, plots_file, min_cid
    try:  # Passes error where min_cid doesn't exist on first code run
        fig.canvas.mpl_disconnect(min_cid)
    except NameError:
        pass
    clear_min(button_idx, max_idx, min_idx, ax, _, tree_min)

    def update_min_value(new_min):
        time_series = np.ravel(plots_file[:, plot_idx])
        max_idx, min_idx = get_current_idxs(plot_idx)

        min_idx[button_idx] = new_min
        new_min_idx = sorted(min_idx, key=nan_sort)
        ax.clear()

        plot_time_series(ax, time_series, var_titles, plot_subtitles)

        plot_events(max_idx, new_min_idx, time_series)
        update_tree(tree_min, new_min_idx, time_series)
        min_idx = new_min_idx
        update_min_matrices(
            min_idx,
            time_series,
            plot_idx,
            all_minidx_matrix,
            all_minval_matrix,
            all_minper_matrix,
            trials,
        )
        canvas.draw_idle()

    def set_min_event(event):
        if event.inaxes and event.button == MouseButton.LEFT:
            time_series = np.ravel(plots_file[:, plot_idx])
            new_event = round(event.xdata)
            possible_indices = np.arange(
                new_event - find_tolerance, new_event + find_tolerance
            )
            possible_indices = possible_indices[
                (possible_indices >= 0) & (possible_indices < len(time_series))
            ]
            try:
                desired_index_within_range = np.argmin(time_series[possible_indices])
            except ValueError:
                messagebox.showwarning(
                    "Warning", "You clicked out of the graph bounds. Please try again."
                )
                return
            desired_index = possible_indices[desired_index_within_range]
            update_min_value(desired_index)
            fig.canvas.mpl_disconnect(min_cid)

    min_cid = fig.canvas.mpl_connect("button_press_event", set_min_event)


def clear_max(button_idx, max_idx, min_idx, ax, tree_max, _):
    global plot_idx, plots_file

    time_series = np.ravel(plots_file[:, plot_idx])
    max_idx, min_idx = get_current_idxs(plot_idx)
    max_idx[button_idx] = np.nan
    new_max_idx = sorted(max_idx, key=nan_sort)
    ax.clear()

    plot_time_series(ax, time_series, var_titles, plot_subtitles)

    plot_events(new_max_idx, min_idx, time_series)
    update_tree(tree_max, new_max_idx, time_series)
    max_idx = new_max_idx
    update_max_matrices(
        max_idx,
        time_series,
        plot_idx,
        all_maxidx_matrix,
        all_maxval_matrix,
        all_maxper_matrix,
        trials,
    )
    canvas.draw_idle()


def clear_min(button_idx, max_idx, min_idx, ax, _, tree_min):
    global plot_idx, plots_file

    time_series = np.ravel(plots_file[:, plot_idx])
    max_idx, min_idx = get_current_idxs(plot_idx)
    min_idx[button_idx] = np.nan
    new_min_idx = sorted(min_idx, key=nan_sort)
    ax.clear()

    plot_time_series(ax, time_series, var_titles, plot_subtitles)

    plot_events(max_idx, new_min_idx, time_series)
    update_tree(tree_min, new_min_idx, time_series)
    min_idx = new_min_idx
    update_min_matrices(
        min_idx,
        time_series,
        plot_idx,
        all_minidx_matrix,
        all_minval_matrix,
        all_minper_matrix,
        trials,
    )
    canvas.draw_idle()


def reset_current(plots_file, ax, plot_idx_history):
    messagebox.showinfo("Info", "This isn't working right now. Try again later!")
    pass
    # result = messagebox.askyesno(
    #     "Reset Plot", "Are you sure you want to reset the current plot?"
    # )
    # if result:
    #     plot_idx_history.remove(plot_idx)
    #     iterate_plot(plots_file, ax, plot_idx_history)
    # pass


def iterate_plot(plots_file, ax, plot_idx_history):
    global plot_idx, trial_counter, all_maxidx_matrix, all_minidx_matrix, all_maxval_matrix, all_minval_matrix, all_maxper_matrix, all_minper_matrix
    time_series = np.ravel(plots_file[:, plot_idx])

    if plot_idx not in plot_idx_history:  # Plot has not happened before
        max_idx, min_idx, _, _ = find_prominent(time_series)
        ax.clear()
        update_tree(tree_max, max_idx, time_series)
        update_tree(tree_min, min_idx, time_series)
        set_plot(ax, time_series)
        ax.relim()
        ax.autoscale_view()
        canvas.draw()
        update_max_matrices(
            max_idx,
            time_series,
            plot_idx,
            all_maxidx_matrix,
            all_maxval_matrix,
            all_maxper_matrix,
            trials,
        )
        update_min_matrices(
            min_idx,
            time_series,
            plot_idx,
            all_minidx_matrix,
            all_minval_matrix,
            all_minper_matrix,
            trials,
        )
        plot_idx_history.add(plot_idx)
    else:  # Plot has happened before
        # Then we need to plot based on existing idx array
        slice_idx = plot_idx // trials
        max_idx = all_maxidx_matrix[:, trial_counter, slice_idx]
        min_idx = all_minidx_matrix[:, trial_counter, slice_idx]
        ax.clear()
        update_tree(tree_max, max_idx, time_series)
        update_tree(tree_min, min_idx, time_series)
        plot_time_series(ax, time_series, var_titles, plot_subtitles)
        plot_events(max_idx, min_idx, time_series)
        ax.relim()
        ax.autoscale_view()
        fig.tight_layout()
        canvas.draw()


def next_plot(plots_file, ax):
    global plot_idx, trial_counter
    plot_idx += 1
    if (
        plot_idx > plots_file.shape[1] - 1
    ):  # Catches when we go forward from the last plot
        plot_idx = 0
        messagebox.showinfo(
            "Event Picking",
            f"You've reached the last plot! Starting from the first plot. Consider saving events now.",
        )
    trial_counter += (
        1  # Counter to identify which column to pick when selecting previous plots
    )
    if trial_counter > trials - 1:
        trial_counter = 0
    iterate_plot(plots_file, ax, plot_idx_history)


def previous_plot(plots_file, ax):
    global plot_idx, trial_counter
    plot_idx -= 1
    if plot_idx < 0:  # Catches when we go backwards from the first plot
        plot_idx = plots_file.shape[1] - 1
    trial_counter -= 1
    if trial_counter < 0:
        trial_counter = trials - 1
    iterate_plot(plots_file, ax, plot_idx_history)


def save_to_csv(file_path, matrices, var_titles):
    with open(file_path, "w", newline="") as csvfile:
        matrix_delim = ["NEXT_MATRIX"]
        writer = csv.writer(csvfile)
        writer.writerow([f"S{subject_in}_C{condition_in}"])
        writer.writerow(
            ["Variable Metadata (Each repeat of variable indicates trial amount):"]
        )
        writer.writerow([var_titles])
        writer.writerow(["NEXT_MATRIX"])

        delim_check = False
        for matrix in matrices:
            if delim_check:
                writer.writerow(matrix_delim)
            else:
                delim_check = True

            for slice_idx in range(matrix.shape[0]):
                for row in matrix[:, :, slice_idx]:
                    writer.writerow(row)


def save_all_events(
    all_maxval_matrix,
    all_maxidx_matrix,
    all_minval_matrix,
    all_minidx_matrix,
    all_maxper_matrix,
    all_minper_matrix,
    subject,
    condition,
    output_path,
    var_titles,
):
    try:
        file_prefix = f"S{subject}_C{condition}"
        max_file_path = os.path.join(output_path, f"{file_prefix}_Maxima.csv")
        min_file_path = os.path.join(output_path, f"{file_prefix}_Minima.csv")

        result = messagebox.askyesno(
            "Save All Events",
            f"Are you sure you want to save all events?\nThis will save events to:\n\t{output_path}\n\nWith filenames:\n\t{file_prefix}_Maxima.csv\n\t{file_prefix}_Minima.csv\nSelecting 'Yes' will return you to the main window upon saving.",
        )

        if result:
            if os.path.isfile(max_file_path) or os.path.isfile(min_file_path):
                overwrite = messagebox.askyesno(
                    "File Exists",
                    "One or more files already exist at this location. Do you want to overwrite them?",
                )
                if not overwrite:
                    messagebox.showinfo("Save Canceled", "Save operation canceled.")
                    return
        if result:
            all_maxidx_matrix = np.round(all_maxidx_matrix)
            all_minidx_matrix = np.round(all_minidx_matrix)
            save_to_csv(
                max_file_path,
                [all_maxval_matrix, all_maxidx_matrix, all_maxper_matrix],
                var_titles,
            )
            save_to_csv(
                min_file_path,
                [all_minval_matrix, all_minidx_matrix, all_minper_matrix],
                var_titles,
            )
            return_to_toolbox()
        else:
            messagebox.showinfo("Save Canceled", "Save operation canceled.")
    except PermissionError:
        messagebox.showerror(
            "Save Failed",
            "You do not have permission to save files here. Perhaps the CSV is open?",
        )
        return


def event_index(plot_idx):
    slice_idx = plot_idx // trials
    remainder = plot_idx % (trials * 3)
    col = remainder % 5
    row = 0

    return (row, col, slice_idx)


def update_max_matrices(
    max_idx,
    time_series,
    plot_idx,
    all_maxidx_matrix,
    all_maxval_matrix,
    all_maxper_matrix,
    trials,
):
    def event_index(plot_idx):
        slice_idx = plot_idx // trials
        remainder = plot_idx % (trials * 3)
        col = remainder % 5
        row = 0

        return (row, col, slice_idx)

    for i, max_index in enumerate(max_idx):
        idx = event_index(plot_idx)
        idx_row = idx[0] + i
        idx = (idx_row, idx[1], idx[2])
        if np.isnan(max_index):
            all_maxidx_matrix[idx] = np.nan
            all_maxval_matrix[idx] = np.nan
            all_maxper_matrix[idx] = np.nan
        else:
            if isinstance(max_index, float):
                max_index = int(max_index)
            all_maxidx_matrix[idx] = max_idx[i].astype(int)
            all_maxval_matrix[idx] = time_series[max_index]
            all_maxper_matrix[idx] = max_idx[i] / len(time_series) * 100


def update_min_matrices(
    min_idx,
    time_series,
    plot_idx,
    all_minidx_matrix,
    all_minval_matrix,
    all_minper_matrix,
    trials,
):
    def event_index(plot_idx):
        slice_idx = plot_idx // trials
        remainder = plot_idx % (trials * 3)
        col = remainder % 5
        row = 0

        return (row, col, slice_idx)

    for i, min_index in enumerate(min_idx):
        idx = event_index(plot_idx)
        idx_row = idx[0] + i
        idx = (idx_row, idx[1], idx[2])
        if np.isnan(min_index):
            all_minidx_matrix[idx] = np.nan
            all_minval_matrix[idx] = np.nan
            all_minper_matrix[idx] = np.nan
        else:
            if isinstance(min_index, float):
                min_index = int(min_index)
            all_minidx_matrix[idx] = min_idx[i].astype(int)
            all_minval_matrix[idx] = time_series[min_index]
            all_minper_matrix[idx] = min_idx[i] / len(time_series) * 100


def get_current_idxs(plot_idx):
    grab_idx = event_index(plot_idx)
    max_idx = all_maxidx_matrix[:, grab_idx[1], grab_idx[2]]
    min_idx = all_minidx_matrix[:, grab_idx[1], grab_idx[2]]
    return max_idx, min_idx


root = ttk.Window()
center_window(root, 1050, 525)

try:
    subject_in = sys.argv[1]  # Takes subject from main script
except IndexError:
    print(
        "Error: This script isn't expected to run directly, please run BiomechanicsToolbox.py instead."
    )
    messagebox.showerror(
        "Error",
        "This script isn't expected to run directly, please run BiomechanicsToolbox.py instead.",
    )
    sys.exit()
condition_in = sys.argv[2]  # Takes condition from main script
plots_file_str = np.load(sys.argv[3])  # Takes data to plot from main script
plots_file = plots_file_str.astype(float)  # Arrives as DATA x Trial+Var x Subject
trials = int(sys.argv[4])  # Takes number of trials from main script
var_titles = sys.argv[5].split()  # Takes variable title from main script
events_out = sys.argv[6]  # Takes output file from main script

plot_idx = 0
trial_counter = 0
plot_idx_history = set()
find_tolerance = 5

time_series = np.ravel(plots_file[:, plot_idx])
raw_plot_subtitles = []
for plot in range(1, plots_file.shape[1] + 1):
    trial_index = (plot - 1) % trials
    trial_title = f"S{subject_in} C{condition_in} T{trial_index + 1}"
    plot_info = f" --> (Plot {plot}/{plots_file.shape[1]})"
    raw_plot_subtitles.append(trial_title + plot_info)
plot_subtitles = list(islice(cycle(raw_plot_subtitles), plots_file.shape[1]))

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
        lambda: reset_current(plots_file, ax, plot_idx_history),
        17,
        1,
        "navigate.TButton",
    ),
    (
        "Next Plot",
        lambda: next_plot(plots_file, ax),
        1,
        2,
        "navigate.TButton",
    ),
    (
        "Previous Plot",
        lambda: previous_plot(plots_file, ax),
        1,
        1,
        "navigate.TButton",
    ),
    (
        "Save All Events",
        lambda: save_all_events(
            all_maxval_matrix,
            all_maxidx_matrix,
            all_minval_matrix,
            all_minidx_matrix,
            all_maxper_matrix,
            all_minper_matrix,
            subject_in,
            condition_in,
            events_out,
            var_titles,
        ),
        17,
        2,
        "save.TButton",
    ),
]

(
    all_maxval_matrix,
    all_maxidx_matrix,
    all_minval_matrix,
    all_minidx_matrix,
    all_maxper_matrix,
    all_minper_matrix,
) = [
    np.full((3, trials, len(var_titles)), np.nan) for _ in range(6)
]  # Creates empty matrices for holding max and min values,indices, percent of trial length (6 total)
fig, ax, canvas = create_figure()
max_idx, min_idx = set_plot(ax, time_series)
general_buttons = []
place_general_buttons(root, general_btn_specs, general_buttons)
set_button_frame(
    root, row=2, column=1, rowspan=25, label_text="Replace", btn_specs=replace_btn_specs
)
set_button_frame(
    root, row=2, column=2, rowspan=25, label_text="Clear", btn_specs=clear_btn_specs
)
tree_max = create_treeview(root, 11, 1, 6, "Event", ("Frame", "Value"), (55, 70))
treeview_contents(tree_max, time_series)
tree_min = create_treeview(root, 11, 2, 6, "Event", ("Frame", "Value"), (55, 70))
treeview_contents(tree_min, time_series)

update_max_matrices(
    max_idx,
    time_series,
    plot_idx,
    all_maxidx_matrix,
    all_maxval_matrix,
    all_maxper_matrix,
    trials,
)
update_min_matrices(
    min_idx,
    time_series,
    plot_idx,
    all_minidx_matrix,
    all_minval_matrix,
    all_minper_matrix,
    trials,
)
plot_idx_history.add(plot_idx)


def return_to_toolbox():
    messagebox.showinfo(
        "Save Successful",
        "Events saved! Returning you to the Biomechanics Toolbox...",
    )
    os.remove("reordered_data.npy")  # Deletes the reordered data file upon window close
    root.destroy()


def close_confirm():
    if messagebox.askyesno(
        "Quit",
        "Are you sure you want to quit? Make sure you have saved your events before proceeding!",
    ):
        os.remove(
            "reordered_data.npy"
        )  # Deletes the reordered data file upon window close
        root.destroy()


root.iconbitmap("BT_Icon.ico")
root.iconbitmap(default="BT_Icon.ico")
root.title("Biomechanics Toolbox - Event Picking")

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=0)
root.protocol("WM_DELETE_WINDOW", close_confirm)
root.bind("<Left>", lambda event: previous_plot(plots_file, ax))
root.bind("<Right>", lambda event: next_plot(plots_file, ax))

root.mainloop()
