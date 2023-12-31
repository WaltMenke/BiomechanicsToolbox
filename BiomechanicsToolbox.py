import tkinter as tk
from tkinter import ttk, filedialog, PhotoImage, messagebox, simpledialog
import ttkbootstrap as ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import sys
import os
import subprocess
import spm1d as spm
import re
import webbrowser
import ToolboxFunctions as tf
from PIL import Image, ImageTk
import openpyxl
import ast

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

##################### Initial Functions ######################


def open_program_docs():
    help_file_path = "BiomechanicsToolbox.docx"
    os.startfile(help_file_path)


def create_label_entry(
    parent,
    label_text,
    width=40,
    side="left",
    fill=None,
    justify="center",
    anchor="center",
    default_val="",
):
    frame = ttk.Frame(parent)
    frame.pack(expand=1, fill=fill)
    label = ttk.Label(frame, text=label_text)
    label.pack(expand=1, side=side, anchor=anchor)
    entry_var = tk.StringVar()
    entry = ttk.Entry(frame, textvariable=entry_var, width=width, justify=justify)
    entry.insert(0, str(default_val))
    entry.pack(expand=1, side=side)
    return entry_var


def execute_function_button(
    parent, ButtonLabel, desired_function, side=None, anchor="center"
):
    style = ttk.Style()
    style.configure(
        "Orange.TButton", foreground="white", background="#FF8200", bordercolor=0
    )
    execute_button = ttk.Button(
        parent,
        text=ButtonLabel,
        command=desired_function,
        style="Orange.TButton",
        cursor="hand2",
    )
    style.map(
        "Orange.TButton",
        foreground=[("pressed", "white"), ("active", "white")],
        background=[("pressed", "gray"), ("active", "#FF8200")],
    )
    execute_button.pack(padx=5, pady=5, side=side, anchor=anchor)
    return execute_button


def create_checkbox(parent, label_text, default_value=False, padx=0, pady=0):
    checkbox_var = tk.BooleanVar(value=default_value)
    checkbox = ttk.Checkbutton(parent, text=label_text, variable=checkbox_var)
    checkbox.pack(expand=1, padx=padx, pady=pady)
    return checkbox_var


def create_dropdown(parent, label_text, options, anchor="n", width=15):
    label = tk.Label(parent, text=label_text)
    label.pack(pady=2.5, anchor=anchor, side="top")

    selected_option = tk.StringVar()
    dropdown = ttk.Combobox(
        parent,
        textvariable=selected_option,
        values=options,
        justify="center",
        width=width,
    )
    dropdown.pack(pady=2.5, anchor=anchor, side="top")
    dropdown.set(options[0])
    return label, dropdown


def browse_in_button(parent, ButtonLabel, desired_function):
    style = ttk.Style()
    style.configure(
        "Green.TButton", foreground="white", background="#228B22", bordercolor=0
    )
    browse_button = ttk.Button(
        parent,
        text=ButtonLabel,
        command=desired_function,
        style="Green.TButton",
        cursor="hand2",
    )
    style.map(
        "Green.TButton",
        foreground=[("pressed", "white"), ("active", "white")],
        background=[("pressed", "gray"), ("active", "#228B22")],
    )
    browse_button.pack(padx=5, pady=5)
    return browse_button


def browse_out_button(parent, ButtonLabel, desired_function):
    style = ttk.Style()
    style.configure(
        "Blue.TButton", foreground="white", background="#0047AB", bordercolor=0
    )
    browse_button = ttk.Button(
        parent,
        text=ButtonLabel,
        command=desired_function,
        style="Blue.TButton",
        cursor="hand2",
    )
    style.map(
        "Blue.TButton",
        foreground=[("pressed", "white"), ("active", "white")],
        background=[("pressed", "gray"), ("active", "#0047AB")],
    )
    browse_button.pack(padx=5, pady=5)
    return browse_button


color_choices = [
    "Black",
    "Blue",
    "Red",
    "Green",
    "Purple",
    "Orange",
    "Yellow",
    "Cyan",
    "Magenta",
    "Grey",
]

##################### Script Gen Tab ######################


def open_scriptgen_tab():
    global script_entry, model_entry, heightweight_entry, script_out_entry
    if check_tab_exists("Script Gen"):
        return
    scriptgen_tab = ttk.Frame(main_tab)
    main_tab.add(scriptgen_tab, text="Script Gen")
    main_tab.select(scriptgen_tab)
    scriptgen_label = tk.Label(
        scriptgen_tab,
        text="This function generates pipelines and models for each subject with the same format \nas the template script supplied, and saves them in a user-specified directory.\n\nNote: Subject number is based on entries in the Height-Weight table.",
    )
    scriptgen_label.pack(anchor="n")

    input_entry = None
    output_entry = None

    def toolbox_scriptgen():
        if not script_entry.get().endswith(".v3s"):
            messagebox.showerror(
                "Input Error",
                f"Script file is '{script_entry.get()}'. Please enter the path to the tf.v3d pipeline file (.v3s).",
                icon="error",
            )
            return
        if not model_entry.get().endswith(".mdh"):
            messagebox.showerror(
                "Input Error",
                f"Model file is '{model_entry.get()}'. Please enter the path to the tf.v3d model file (.mdh).",
                icon="error",
            )
            return
        if not heightweight_entry.get().endswith(".xlsx"):
            messagebox.showerror(
                "Input Error",
                f"Height-Weight file is '{heightweight_entry.get()}'. Please enter the path to the Height-Weight file (.xlsx).",
                icon="error",
            )
            return
        tf.generate_scripts(
            script_entry.get(),
            model_entry.get(),
            heightweight_entry.get(),
            output_entry.get(),
        )

    def script_template_direc():
        script_direc = filedialog.askopenfilename(
            title="Select Script Template",
            multiple=False,
            filetypes=(("tf.v3d Pipeline", "*.v3s"),),
        )
        if not script_direc:
            return
        if script_direc:
            script_entry.set(script_direc)

    def model_template_direc():
        model_direc = filedialog.askopenfilename(
            title="Select Model Template",
            multiple=False,
            filetypes=(("tf.v3d Model", "*.mdh"),),
        )
        if not model_direc:
            return
        if model_direc:
            model_entry.set(model_direc)

    def height_weight():
        heightweight_direc = filedialog.askopenfilename(
            title="Select Height-Weight File",
            multiple=False,
            filetypes=(("Excel", "*.xlsx"),),
        )
        if not heightweight_direc:
            return
        if heightweight_direc:
            heightweight_entry.set(heightweight_direc)

    def script_out_direc():
        out_direc = filedialog.askdirectory(
            title="Select Output Directory", initialdir=input_entry
        )
        if not out_direc:
            return
        if out_direc:
            script_out_entry.set(out_direc)

    script_frame = ttk.Frame(scriptgen_tab)
    script_frame.pack(expand=1)

    script_entry = create_label_entry(script_frame, "Script Template File:", 80, "top")
    browse_in_button(script_frame, "Browse", script_template_direc)

    model_entry = create_label_entry(script_frame, "Model Template File:", 80, "top")
    browse_in_button(script_frame, "Browse", model_template_direc)

    heightweight_entry = create_label_entry(
        script_frame, "Height-Weight Table:", 80, "top"
    )
    browse_in_button(script_frame, "Browse", height_weight)

    script_out_entry = create_label_entry(
        script_frame, "Script Output Directory:", 80, "top"
    )
    browse_out_button(script_frame, "Browse", script_out_direc)

    execute_function_button(script_frame, "Generate Scripts", toolbox_scriptgen)


##################### EMG Tab ######################


def open_emg_tab():
    if check_tab_exists("EMG"):
        return
    emg_tab = ttk.Frame(main_tab)
    main_tab.add(emg_tab, text="EMG")
    main_tab.select(emg_tab)
    emg_label = tk.Label(
        emg_tab,
        text="This function allows you to filter and process EMG and optionally produce graphs.",
    )
    emg_label.pack(fill="x", anchor="n", expand=True)


def save_emg():
    with open("EMG_Params.txt", "w") as file:
        pass


##################### Batch Tab ######################


def open_batch_tab():
    global batch_in_entry, batch_out_entry, batch_components_entry, batch_search_entry, batch_trials, batch_file_savename, batch_normalized
    if check_tab_exists("Batch"):
        return
    batch_tab = ttk.Frame(main_tab)
    main_tab.add(batch_tab, text="Batch")
    main_tab.select(batch_tab)
    batch_label = tk.Label(
        batch_tab,
        text="This function creates a 3D NumPy array of data points (dimension 1), variables and trials (dimension 2),\nand subjects (dimension 3) from a list of tf.v3d output files for event picking or quality checking.\n\nNote: Non-normalized inputs (default) will have rows equal to the largest row amount across all files.\nNaN will fill extra spaces in other trials.",
    )
    batch_label.pack(fill="x", expand=True, anchor="n")

    def toolbox_batch():
        components_in = batch_components_entry.get()
        if components_in == "" or "," not in components_in:
            messagebox.showerror(
                "Input Error",
                "Please enter a comma-separated list of components\nExample: To denote X,Y and not Z, enter '1,1,0'.",
                icon="error",
            )
            return
        if (
            batch_search_entry.get() == ""
        ):  # if not set, default is ALL text files in folder
            batch_search_entry.set(".txt")
        components = components_in.split(",")
        X = int(components[0])
        Y = int(components[1])
        Z = int(components[2])
        tf.batch(
            batch_in_entry.get(),
            batch_search_entry.get(),
            batch_out_entry.get(),
            batch_file_savename.get(),
            batch_trials.get(),
            X,
            Y,
            Z,
            batch_normalized.get(),
        )
        messagebox.showinfo(
            "Batch Successful",
            f"Data has been compiled here: {batch_out_entry.get()}",
        )

    def batch_in():
        in_direc = filedialog.askdirectory(
            title="Select V3D Data Inputs",
        )
        if not in_direc:
            return
        if in_direc:
            batch_in_entry.set(in_direc)

    def batch_out():
        out_direc = filedialog.askdirectory(initialdir=batch_in_entry)
        if not out_direc:
            return
        if out_direc:
            batch_out_entry.set(out_direc)

    batch_frame = ttk.Frame(batch_tab)
    batch_frame.pack(expand=1, side="top")
    batch_in_entry = create_label_entry(batch_frame, "V3D Data Inputs:", 80, "top")
    browse_in_button(batch_frame, "Browse", batch_in)
    batch_out_entry = create_label_entry(batch_frame, "Output Directory:", 80, "top")
    browse_out_button(batch_frame, "Browse", batch_out)
    batch_normalized = create_checkbox(batch_frame, "Inputs Normalized:", False, 0, 10)

    batch_sub_left = ttk.Frame(batch_frame)
    batch_sub_left.pack(side="left")
    batch_trials = create_label_entry(batch_sub_left, "Trials per Subject:", 5, "top")
    batch_search_entry = create_label_entry(
        batch_sub_left, "String to Search:", 30, "top"
    )

    batch_sub_right = ttk.Frame(batch_frame)
    batch_sub_right.pack(side="right")
    batch_components_entry = create_label_entry(
        batch_sub_right, "Component Amount (X, Y, Z):", 5, "top"
    )
    batch_file_savename = create_label_entry(
        batch_sub_right, "File Save Name:", 30, "top"
    )

    execute_function_button(batch_frame, "Batch Process", toolbox_batch, side="bottom")


##################### Normalize Tab ######################
def open_normalize_tab():
    global norm_in, norm_out
    if check_tab_exists("Normalize"):
        return
    normalize_tab = ttk.Frame(main_tab)
    main_tab.add(normalize_tab, text="Normalize")
    main_tab.select(normalize_tab)
    normalize_label = tk.Label(
        normalize_tab,
        text="This function allows you to normalize the length of all trials and variables\nfor non-normalized batch processed data.",
    )

    def normalize_in():
        in_direc = filedialog.askopenfilename(
            title="Select Batched Data File",
            filetypes=(("TXT Files", "*.txt"),),
            multiple=False,
        )
        if not in_direc:
            return
        if in_direc:
            norm_in.set(in_direc)

    def normalize_out():
        out_direc = filedialog.askdirectory(
            title="Select Output Directory", initialdir=norm_in
        )
        if not out_direc:
            return
        if out_direc:
            norm_out.set(out_direc)

    def toolbox_normalize():
        tf.normalize(norm_in.get(), norm_out.get())

    normalize_label.pack(fill="x", anchor="n", expand=True)
    normalize_frame = ttk.Frame(normalize_tab)
    normalize_frame.pack(expand=1, side="top", anchor="n")
    norm_in = create_label_entry(normalize_frame, "Batched Data File:", 80, "top")
    browse_in_button(normalize_frame, "Browse", normalize_in)
    norm_out = create_label_entry(normalize_frame, "Output Directory:", 80, "top")
    browse_out_button(normalize_frame, "Browse", normalize_out)
    execute_function_button(normalize_frame, "Normalize Data", toolbox_normalize)


##################### Quality Check Tab ######################
def open_quality_check_tab():
    global qual_in, qual_subs
    if check_tab_exists("Quality Check"):
        return
    quality_check_tab = ttk.Frame(main_tab)
    main_tab.add(quality_check_tab, text="Quality Check")
    main_tab.select(quality_check_tab)
    quality_check_label = tk.Label(
        quality_check_tab,
        text="This function takes an import from 'Batch' and allows the user to select at least one subject\nto plot all variable data to identify outliers and problematic trials.\n\nNote: Subject Numbers should be comma-separated. Alternatively, type 'All'.\nWarning: Typing 'All' may take a long time to run and is not advisable for older hardware.",
    )
    quality_check_label.pack(fill="none", expand=False, anchor="n")
    plots_out = []

    def quality_directory():
        in_direc = filedialog.askopenfilename(
            title="Select Batched Data File",
            filetypes=(("TXT Files", "*.txt"),),
            multiple=False,
        )
        if not in_direc:
            return
        if in_direc:
            qual_in.set(in_direc)

    def toolbox_quality_check():
        nonlocal plots_out

        qual_check_in = qual_in.get()
        if not qual_in.get():
            messagebox.showerror(
                "Input Error", "Please select a batched data file.", icon="error"
            )
            return

        if not qual_subs.get():
            messagebox.showerror(
                "Input Error", "Please specify at least one subject.", icon="error"
            )
            return

        if qual_subs.get() == "All":
            _, sub_count = tf.qual_metadata(qual_check_in)
            subject_idx = range(0, sub_count)
        else:
            sub_num = len(qual_subs.get().split(","))
            # _, sub_count = tf.qual_metadata(qual_check_in)
            # if sub_count not in range(sub_num + 1):
            #     messagebox.showerror(
            #         "Input Error",
            #         "Please specify a valid number of subjects.",
            #         icon="error",
            #     )
            #     return
            if sub_num == 1:
                subject_num = qual_subs.get()
            else:
                subject_num = qual_subs.get().split(",")
            subject_idx = [int(x) - 1 for x in subject_num]
        for sub in range(0, len(subject_idx)):
            plots_out += tf.quality_check(qual_check_in, int(subject_idx[sub]))
        qual_plot_num = 0

        def exit_qual(qual_window):
            qual_window.destroy()

        def save_current_qual(plots_out, qual_plot_num):
            save_path = filedialog.asksaveasfilename(
                title="Save Quality Check",
                initialdir=qual_in,
                initialfile=f"Quality Check {qual_plot_num + 1}.pdf",
                defaultextension=".pdf",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("JPG files", "*.jpg"),
                    ("PNG files", "*.png"),
                    (".TIF files", "*.tif"),
                ],
            )
            if not save_path:
                messagebox.showinfo("Quality Check", "Save operation canceled by user.")
                return
            plots_out[qual_plot_num].savefig(save_path)
            messagebox.showinfo(
                "Quality Check",
                f"One quality check has been saved here: {save_path}",
            )

        def save_all_quals(plots_out):
            save_path = filedialog.asksaveasfilename(
                title="Save All Quality Checks",
                initialdir=qual_in,
                initialfile="All Quality Checks.pdf",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
            )
            if not save_path:
                messagebox.showinfo("Quality Check", "Save operation canceled by user.")
                return
            with PdfPages(save_path) as pdf:
                for plot in plots_out:
                    pdf.savefig(plot, bbox_inches="tight")
            messagebox.showinfo(
                "Quality Check",
                f"All quality checks have been saved here: {save_path}",
            )

        class QualityPlot(tk.Frame):
            def __init__(self, master, plots_out, **kwargs):
                super().__init__(master, **kwargs)

                self.plots = []
                self.qual_plot_num = 0
                self.columnconfigure(0, weight=1)
                self.rowconfigure(0, weight=1)
                for plot in plots_out:
                    frm = tk.Frame(self)
                    canvas = FigureCanvasTkAgg(figure=plot, master=frm)
                    canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
                    frm.grid(row=0, column=0, sticky="nsew")
                    self.plots.append(frm)
                self.plots[self.qual_plot_num].tkraise()

            def next_plot(self):
                if self.qual_plot_num == len(plots_out) - 1:
                    return
                self.qual_plot_num += 1
                self.plots[self.qual_plot_num].tkraise()

            def previous_plot(self):
                if self.qual_plot_num == 0:
                    return
                self.qual_plot_num -= 1
                self.plots[self.qual_plot_num].tkraise()

        qual_window = ttk.Window()
        qual_window.resizable(True, True)
        qual_window.title("Biomechanics Toolbox - Quality Checking")
        qual_window.iconbitmap("BT_Icon.ico")
        center_window(qual_window, 1100, 1100)

        canvas = QualityPlot(qual_window, plots_out)
        canvas.pack(expand=0, fill="none")

        next_button = ttk.Button(
            qual_window,
            text="Next\n--->",
            command=canvas.next_plot,
        )
        next_button.pack(side=tk.RIGHT)

        previous_button = ttk.Button(
            qual_window,
            text="Previous\n <---",
            command=canvas.previous_plot,
        )
        previous_button.pack(side=tk.LEFT)

        qual_menubar = ttk.Menu(master=qual_window)
        qualMenu = ttk.Menu(qual_menubar)
        qualMenu.add_command(
            label="Save Current",
            command=lambda: save_current_qual(plots_out, qual_plot_num),
        )
        qualMenu.add_command(
            label="Save All", command=lambda: save_all_quals(plots_out)
        )
        qualMenu.add_command(label="Exit", command=lambda: exit_qual(qual_window))
        qual_menubar.add_cascade(label="File", menu=qualMenu)
        qual_window.config(menu=qual_menubar)

    quality_frame = ttk.Frame(quality_check_tab)
    quality_frame.pack(expand=1)

    qual_in = create_label_entry(
        quality_frame, "Batched Data Input Directory:", 80, "top", None, "center", "n"
    )
    browse_in_button(quality_frame, "Browse", quality_directory)
    qual_subs = create_label_entry(
        quality_frame, "Subject Numbers:", 10, "top", None, "center", "n"
    )
    execute_function_button(
        quality_frame, "Check Quality", toolbox_quality_check, "top", "n"
    )


##################### Event Pick Tab ######################
def open_eventpick_tab():
    if check_tab_exists("Event Pick"):
        return
    eventpick_tab = ttk.Frame(main_tab)
    main_tab.add(eventpick_tab, text="Event Pick")
    main_tab.select(eventpick_tab)
    eventpick_label = tk.Label(
        eventpick_tab,
        text="This function allows you to pick discrete events from a batched output file.\nNote: Select ONE subject and ONE condition.",
    )
    eventpick_label.pack(fill="x", anchor="n", expand=True)

    # def create_eventplot_info(data_cube, subject, condition, var_list, components):
    #     true_vars = list(set(var_list))
    #     trials = int(data_cube.shape[1] / len(var_list))

    #     plot_titles = []
    #     for var_idx in range(len(true_vars)):
    #         for comp_idx in range(len(components)):
    #             for trial_idx in range(trials):
    #                 plot_titles.append(
    #                     f"S{subject}C{condition}T{trial_idx+1}  {true_vars[var_idx]} {components[comp_idx]}"
    #                 )
    #     column_indices = []
    #     for set_index in range(trials):
    #         for i in range(true_vars):
    #             index = set_index * true_vars + i
    #             if index < data_cube.shape[1]:
    #                 column_indices.append(index)
    #     return plot_titles, column_indices

    def toolbox_eventpick(data_in, data_out):
        if data_in == "" or data_out == "":
            tk.messagebox.showerror(
                "Error", "Input and/or Output cannot be empty strings.", icon="error"
            )
            return
        if not os.path.exists(data_in):
            tk.messagebox.showerror(
                "Error", f"Input '{data_in}' does not exist.", icon="error"
            )
            return
        if not os.path.exists(data_out):
            os.makedirs(data_out)
        var_bool_array = set_var_selection(
            event_listbox
        )  # returns a list of booleans corresponding to the selected variables
        event_vars = [
            item
            for item, selected in zip(event_listbox.get(0, "end"), var_bool_array)
            if selected
        ]  # uses the list of booleans as a mask on all variables present in the file
        flattened_vars = [
            item.strip() for sublist in event_vars for item in sublist.split(",")
        ]  # flattens the list of lists
        pattern = re.compile(r"\s*\(\d+\)")  # regex pattern
        stripped_vars = [
            re.sub(pattern, "", var) for var in flattened_vars
        ]  # applies regex pattern
        data_cube, file_vars, _, components = tf.batch_reshape(
            data_in
        )  # reshapes the input data
        trials = int(data_cube.shape[1] / len(var_bool_array))  # number of trials
        sub_titles = []  # list of subjects
        var_titles = []  # list of variables

        for var_idx in range(sum(var_bool_array)):  # for each variable selected
            for trial_idx in range(trials):  # for each trial
                sub_titles.append(
                    f"S{int(subject_idx.get())}C{int(condition_in.get())}T{trial_idx+1}"
                )  # creates plot titles, such as "S1C1T1"
                var_titles.append(
                    f"{str(stripped_vars[var_idx])}"
                )  # creates plot subtitles
        data_to_plot = np.full(
            (
                data_cube.shape[0],
                (sum(var_bool_array) * trials),
                1,
            ),
            np.nan,
        )  # creates an empty array to fill with data
        var_bool_array = np.array(var_bool_array)  # converts list to array

        for i in range(trials):  # for each trial
            start_col = i * len(
                var_bool_array
            )  # start column, based on amount of variables
            end_col = (i + 1) * len(var_bool_array)  # end column
            selected_columns = data_cube[
                :, start_col:end_col, int(subject_idx.get()) - 1
            ][
                :, var_bool_array.astype(bool), None
            ]  # uses boolean mask to select columns
            data_to_plot[
                :, i * sum(var_bool_array) : (i + 1) * sum(var_bool_array)
            ] = selected_columns  # fills the empty array with the selected columns

    def raw_data_direc():
        in_direc = filedialog.askopenfilename(
            title="Select Raw Data File",
            filetypes=(("TXT Files", "*.txt"),),
            multiple=False,
        )
        if not in_direc:
            return
        if in_direc:
            data_in.set(in_direc)
            event_listbox_gen(data_in.get(), event_listbox)

    def events_out_direc():
        out_direc = filedialog.askdirectory(
            title="Select Output Directory", initialdir=data_in
        )
        if not out_direc:
            return
        if out_direc:
            data_out.set(out_direc)

    def set_var_selection(listbox):
        if listbox.size() == 0:
            return []
        count = listbox.size()
        selected_indices = listbox.curselection()
        bool_array = [1 if i in selected_indices else 0 for i in range(count)]
        return bool_array

    def on_listbox_select(listbox):
        def select_handler(event):
            if listbox.size() == 0:
                return
            selected_indices = listbox.curselection()
            selected_items = [listbox.get(index) for index in selected_indices]

        return select_handler

    def event_listbox_gen(normalized_data, listbox):
        _, var_list, _, comp_list = tf.batch_reshape(normalized_data)
        appended_vars = []
        for i in range(len(var_list)):
            current_xyz = comp_list[i % len(comp_list)]
            appended_vars.append(
                var_list[i] + " " + current_xyz + " (" + str(i + 1) + ")"
            )
        listbox.delete(0, tk.END)
        for var in appended_vars:
            listbox.insert(tk.END, var)

    eventpick_frame = ttk.Frame(eventpick_tab)
    eventpick_frame.pack(expand=1)

    box_label = tk.Label(
        eventpick_frame,
        text="Detected Variables:",
    )
    box_label.pack(side=tk.TOP, padx=10, pady=0)
    event_listbox = tk.Listbox(eventpick_frame, selectmode=tk.MULTIPLE)
    event_listbox.pack(side=tk.TOP, padx=10, pady=0)
    event_listbox.bind("<<ListboxSelect>>", on_listbox_select(event_listbox))

    data_in = create_label_entry(eventpick_frame, "Batched Data File:", 80, "top")
    browse_in_button(eventpick_frame, "Browse", raw_data_direc)
    data_out = create_label_entry(
        eventpick_frame, "Events Output Directory:", 80, "top"
    )
    browse_out_button(eventpick_frame, "Browse", events_out_direc)
    subject_idx = create_label_entry(
        eventpick_frame, "Subject Number (enter ONE):", 10, "top"
    )
    condition_in = create_label_entry(
        eventpick_frame, "Condition Number (enter ONE)):", 10, "top"
    )
    execute_function_button(
        eventpick_frame,
        "Pick Events",
        lambda: toolbox_eventpick(data_in.get(), data_out.get()),
    )


def save_eventpick():
    with open("EventPick_Params.txt", "w") as file:
        pass


##################### Event Compile Tab ######################
def open_eventcompile_tab():
    if check_tab_exists("Event Compile"):
        return
    stats_tab = ttk.Frame(main_tab)
    main_tab.add(stats_tab, text="Event Compile")
    main_tab.select(stats_tab)
    stats_label = tk.Label(
        stats_tab,
        text="This function allows you to gather your picked events in table outputs.",
    )
    stats_label.pack(fill="x", anchor="n", expand=True)


def save_eventcompile():
    with open("EventCompile_Params.txt", "w") as file:
        pass


##################### Ensemble Tab ######################
def open_ensemble_tab():
    global ensemble_in, ensemble_out, ens_variables_listbox, ens_axes_listbox, ensemble_dpi, ens_mean_color, ens_std_color, y_line_var
    if check_tab_exists("Ensemble"):
        return
    ensemble_tab = ttk.Frame(main_tab)
    main_tab.add(ensemble_tab, text="Ensemble")
    main_tab.select(ensemble_tab)
    ensemble_label = tk.Label(
        ensemble_tab,
        text="This function allows you to create ensemble curves of specific\nnormalized variables that are of publication quality.\nNote: Double click on list items to edit them.",
    )
    ensemble_label.pack(fill="x", anchor="n", expand=True)

    def ensemble_in_direc(event=None):
        in_direc = filedialog.askopenfilename(
            title="Select Batched Data File",
            filetypes=(("TXT Files", "*.txt"),),
            multiple=False,
        )
        if not in_direc:
            return
        if in_direc:
            ensemble_in.set(in_direc)
            var_listbox(ensemble_in.get(), ens_variables_listbox, ens_axes_listbox)

    def var_listbox(normalized_data, listbox_a, listbox_b):
        _, var_list, _, comp_list = tf.batch_reshape(normalized_data)
        appended_vars = []
        for i in range(len(var_list)):
            current_xyz = comp_list[i % len(comp_list)]
            appended_vars.append(
                var_list[i] + " " + current_xyz + " (" + str(i + 1) + ")"
            )
        listbox_a.delete(0, tk.END)
        for var in appended_vars:
            listbox_a.insert(tk.END, var)

        listbox_b.delete(0, tk.END)
        axes_list = []
        for i in range(len(appended_vars)):
            axes_list.append(f"X-Axis, Y-Axis ({i+1})")
        for var in axes_list:
            listbox_b.insert(tk.END, var)
        return appended_vars

    def ensemble_out_direc():
        out_direc = filedialog.askdirectory(
            title="Select Output Directory", initialdir=ensemble_in
        )
        if not out_direc:
            return
        if out_direc:
            ensemble_out.set(out_direc)

    def on_scroll(*args):
        ens_variables_listbox_scroll(*args)
        ens_axes_listbox_scroll(*args)

    def ens_variables_listbox_scroll(event):
        fraction = -1 * (event.delta / 120)
        ens_variables_listbox.yview_scroll(int(fraction), "units")
        ens_axes_listbox.yview_scroll(int(fraction) * 5, "units")

    def ens_axes_listbox_scroll(event):
        fraction = -1 * (event.delta / 120)
        ens_variables_listbox.yview_scroll(int(fraction) * 5, "units")
        ens_axes_listbox.yview_scroll(int(fraction), "units")

    def on_listbox_select(listbox):
        def select_handler(event):
            if listbox.size() == 0:
                return
            selected_indices = listbox.curselection()
            selected_items = [listbox.get(index) for index in selected_indices]

        return select_handler

    def on_double_click(listbox):
        def double_click_handler(event):
            if listbox.size() == 0:
                return
            selected_index = listbox.nearest(event.y)
            replacement_text = ask_for_replacement_text()
            if replacement_text is not None:
                listbox.delete(selected_index)
                listbox.insert(selected_index, replacement_text)

        return double_click_handler

    def ask_for_replacement_text():
        replacement_text = simpledialog.askstring(
            f"Replace Text", "Replace entry with:"
        )
        if not replacement_text:
            return None
        return replacement_text

    def y_line_check():
        value = y_line_var.get()

    def set_var_selection(listbox):
        if listbox.size() == 0:
            return []
        count = listbox.size()
        selected_indices = listbox.curselection()
        bool_array = [1 if i in selected_indices else 0 for i in range(count)]
        return bool_array

    def toolbox_ensemble(ensemble_in, ensemble_out):
        try:
            if not os.path.exists(ensemble_out):
                result = messagebox.askyesno(
                    "Directory Error",
                    "No directory with that name. Create it?",
                    icon="question",
                )
                if result:
                    os.makedirs(ensemble_out)
            if ensemble_in == "":
                raise ValueError("No input directory selected.")
            if ensemble_out == "":
                raise ValueError("No output directory selected.")
            if 299 >= int(ensemble_dpi.get()) < 801:
                raise ValueError(
                    "DPI value must be greater than 300 and less than 800."
                )
            var_bool_array = set_var_selection(ens_variables_listbox)
            if sum(var_bool_array) == 0:
                raise ValueError("No variables selected. Make sure they are selected!")
            axes = [
                item
                for item, selected in zip(
                    ens_axes_listbox.get(0, "end"), var_bool_array
                )
                if selected
            ]
            selected_vars = [
                item
                for item, selected in zip(
                    ens_variables_listbox.get(0, "end"), var_bool_array
                )
                if selected
            ]
            norm_cube, _, _, _ = tf.batch_reshape(ensemble_in)

            if norm_cube.ndim != 3:
                raise ValueError(
                    "Data input does not have 3 dimensions. Check the tf.batch() function output."
                )
            are_floats = np.all(np.isfinite(norm_cube))  # Check for NaNs
            if not are_floats:
                raise ValueError(
                    "Data input contains NaNs. Check the tf.batch() function output."
                )
            if norm_cube.shape[0] != 101:
                raise ValueError(
                    "This data doesn't look normalized to 101 data points. Check the tf.batch/tf.normalize function output."
                )
            ensemble_means, ensemble_std = tf.process_cube(norm_cube, var_bool_array)

            if "ensemble_means" not in locals() or np.size(ensemble_means) == 0:
                raise ValueError(
                    "Ensemble_means is either not defined or has size 0. Check the tf.process_cube() function."
                )
            if "ensemble_std" not in locals() or np.size(ensemble_std) == 0:
                raise ValueError(
                    "Ensemble_std is either not defined or has size 0. Check the tf.process_cube() function."
                )

            flattened_axes = [
                item.strip() for sublist in axes for item in sublist.split(",")
            ]
            x_axes = flattened_axes[0::2]
            y_axes = flattened_axes[1::2]
            plots_out = []
            for i in range(sum(var_bool_array)):
                plots_out.append(
                    tf.ensemble_plot(
                        ensemble_means[:, i],
                        ensemble_std[:, i],
                        mean_color=str(ens_mean_color.get()),
                        std_color=str(ens_std_color.get()),
                        title=f"{selected_vars[i]}",
                        xlabel=f"{x_axes[i]}",
                        ylabel=f"{y_axes[i]}",
                        legend_labels=["Mean", "Std Dev"],
                        y_line=y_line_var.get(),
                    )
                )
            if plots_out == []:
                raise ValueError(
                    "Plots_out is empty. Check the tf.ensemble_plot() function."
                )
            for i, (fig, _) in enumerate(plots_out):
                output_tiff_path = os.path.join(
                    ensemble_out, f"{selected_vars[i]}.tiff"
                )
                if os.path.exists(output_tiff_path):
                    response = messagebox.askyesno(
                        "File Already Exists",
                        f"The file {output_tiff_path} already exists. Do you want to overwrite it?",
                        icon="question",
                    )
                    if not response:
                        continue
                fig.set_size_inches(4.5, 3.5)
                fig.savefig(
                    output_tiff_path,
                    format="tiff",
                    dpi=int(ensemble_dpi.get()),
                    bbox_inches="tight",
                )
                plt.close(fig)
            messagebox.showinfo(
                "Save Complete",
                f"All ensemble plots have been saved here: {ensemble_out}",
            )
        except ValueError as e:
            tk.messagebox.showerror("Value Error", str(e))
            return

    label_frame = ttk.Frame(ensemble_tab)
    label_frame.pack(expand=1, side="top", anchor="n")
    box1_label = tk.Label(label_frame, text="Detected Variables:")
    box1_label.pack(side=tk.LEFT, padx=30, pady=0)
    box2_label = tk.Label(label_frame, text="Axes Titles:")
    box2_label.pack(side=tk.LEFT, padx=60, pady=0)

    box_frame = ttk.Frame(ensemble_tab)
    box_frame.pack(expand=1, side="top", anchor="n")
    scrollbar = tk.Scrollbar(box_frame, orient="vertical", command=on_scroll)

    ens_variables_listbox = tk.Listbox(
        box_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set
    )
    ens_variables_listbox.pack(side=tk.LEFT, padx=10, pady=0)
    ens_variables_listbox.bind("<MouseWheel>", ens_variables_listbox_scroll)
    ens_variables_listbox.bind(
        "<<ListboxSelect>>", on_listbox_select(ens_variables_listbox)
    )
    ens_variables_listbox.bind(
        "<Double-Button-1>", on_double_click(ens_variables_listbox)
    )
    scrollbar.pack(side=tk.LEFT, fill="y")
    ens_axes_listbox = tk.Listbox(
        box_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set
    )
    ens_axes_listbox.pack(side=tk.LEFT, padx=10, pady=0)
    ens_axes_listbox.bind("<MouseWheel>", ens_axes_listbox_scroll)
    ens_axes_listbox.bind("<<ListboxSelect>>", on_listbox_select(ens_axes_listbox))
    ens_axes_listbox.bind("<Double-Button-1>", on_double_click(ens_axes_listbox))
    scrollbar.config(command=ens_variables_listbox.yview)

    def create_label_entry_pair(parent, label_text, entry_default, side="left"):
        frame = ttk.Frame(parent)
        frame.pack(side="left", padx=10, pady=2.5)

        label = ttk.Label(frame, text=label_text)
        label.pack(side=side)

        entry_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=entry_var, width=8, justify="center")
        entry.insert(0, entry_default)
        entry.pack(side="bottom")

        return entry_var

    options_frame = ttk.Frame(ensemble_tab)
    options_frame.pack(expand=1, side="top", anchor="n")
    ensemble_dpi = create_label_entry_pair(
        options_frame,
        "TIFF DPI:",
        "300",
    )
    ensemble_dpi.set("300")

    mean_label, ens_mean_color = create_dropdown(
        options_frame, "Mean Color:", color_choices, "center", 10
    )
    ens_mean_color.set(color_choices[0])
    std_label, ens_std_color = create_dropdown(
        options_frame, "Std Color:", color_choices, "center", 10
    )
    ens_std_color.set(color_choices[0])

    mean_label.pack(side="left", padx=5)
    ens_mean_color.pack(side="left", padx=5)
    std_label.pack(side="left", padx=5)
    ens_std_color.pack(side="left", padx=5)

    y_line_frame = ttk.Frame(ensemble_tab)
    y_line_frame.pack(side="top")
    y_line_var = tk.BooleanVar()
    y_line_box = ttk.Checkbutton(
        y_line_frame,
        text="Y Line at 0?",
        variable=y_line_var,
        command=lambda: y_line_check(),
    )
    y_line_box.pack(side="bottom")

    ensemble_frame = ttk.Frame(ensemble_tab)
    ensemble_frame.pack(expand=1, side="bottom", anchor="s")
    ensemble_in = create_label_entry(
        ensemble_frame,
        "Normalized Data File:",
        80,
        "top",
        None,
        "center",
        "n",
    )
    browse_in_button(ensemble_frame, "Browse", lambda: ensemble_in_direc())

    ensemble_out = create_label_entry(
        ensemble_frame, "Output Directory:", 80, "top", None, "center", "n"
    )
    browse_out_button(ensemble_frame, "Browse", lambda: ensemble_out_direc())
    execute_function_button(
        ensemble_frame,
        "Create Ensembles",
        lambda: toolbox_ensemble(ensemble_in.get(), ensemble_out.get()),
    )


##################### SPM Tab ######################
def open_spm_tab():
    global selected_group, group_names, group_dropdown, test_dropdown, entry_boxes, output_box, alpha, equal_var, two_tail, spm_dpi, dropdowns, spm_x_label, spm_y_box
    if check_tab_exists("SPM"):
        return
    spm_tab = ttk.Frame(main_tab)
    main_tab.add(spm_tab, text="SPM")
    main_tab.select(spm_tab)
    spm_label = tk.Label(
        spm_tab,
        text="This function allows you to use the spm1d package to compare one\nor more groups with a variety of statistical tests.",
    )

    spm_label.pack(fill="x", anchor="n", expand=True)

    dropdown_frame = ttk.Frame(spm_tab)
    dropdown_frame.pack(fill="x", anchor="n", expand=True)

    entry_frame = ttk.Frame(spm_tab)
    entry_frame.pack(fill="x", anchor="n", expand=True)

    def group_in(entry):
        file_path = filedialog.askopenfilename(
            title="Select Group File",
            multiple=False,
            filetypes=(("Text Files", "*.txt"),),
        )
        if not file_path:
            return
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)

    def group_out(entry):
        file_path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=entry.get(),
        )
        if not file_path:
            return
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)

    def create_entry_in(parent, labels):
        entry_labels = []
        entry_boxes = []
        entry_buttons = []

        for label_text in labels:
            label = tk.Label(parent, text=label_text)
            entry = tk.Entry(parent, width=80, justify="center")
            button = tk.Button(
                parent,
                text="Browse",
                command=lambda entry=entry: group_in(entry),
                background="#228B22",
                foreground="white",
                activebackground="#228B22",
                activeforeground="white",
            )

            label.pack(side="top", padx=5)
            entry.pack(side="top", padx=5)
            button.pack(side="top", padx=5)

            entry_labels.append(label)
            entry_boxes.append(entry)
            entry_buttons.append(button)

        return entry_labels, entry_boxes, entry_buttons

    def create_entry_out(parent, labels):
        entry_labels = []
        entry_boxes = []
        entry_buttons = []

        for label_text in labels:
            label = tk.Label(parent, text=label_text)
            entry = tk.Entry(parent, width=80, justify="center")
            button = tk.Button(
                parent,
                text="Browse",
                command=lambda entry=entry: group_out(entry),
                background="#0047AB",
                foreground="white",
                activebackground="#0047AB",
                activeforeground="white",
            )

            label.pack(side="top", padx=5)
            entry.pack(side="top", padx=5)
            button.pack(side="top", padx=5)

            entry_labels.append(label)
            entry_boxes.append(entry)
            entry_buttons.append(button)

        return entry_labels, entry_boxes, entry_buttons

    def on_option_selected(event, dropdown):
        selected_option_value = group_dropdown.get()

    def center_options_window(window):
        original_width = root.winfo_width()
        original_height = root.winfo_height()
        percentage_width = 0.4
        percentage_height = 0.85
        second_width = int(original_width * percentage_width)
        second_height = int(original_height * percentage_height)
        x = root.winfo_x() - second_width
        y = root.winfo_y()
        window.geometry(f"{second_width}x{second_height}+{x}+{y}")

    options = None

    def on_group_selected(event):
        global selected_group, group_names, group_dropdown, test_dropdown, entry_boxes, output_box, alpha, equal_var, two_tail, spm_dpi, dropdowns, spm_x_label, spm_y_box
        nonlocal options
        selected_group = group_dropdown.get()

        if options is not None:
            options.destroy()
        options = ttk.Toplevel(spm_tab)
        options.title("")
        center_options_window(options)
        title = ttk.Label(
            options,
            text="Additional SPM Parameters",
            font=("Helvetica", 10, "underline"),
        )
        title.pack()

        alpha = create_label_entry(
            parent=options,
            label_text="Alpha Level:",
            width=8,
            default_val=0.05,
            side="top",
        )
        equal_var = create_checkbox(
            parent=options, label_text="Equal Variance", default_value=False
        )
        two_tail = create_checkbox(
            parent=options, label_text="Two Tailed", default_value=True
        )
        spm_dpi = create_label_entry(
            parent=options,
            label_text="TIFF DPI:",
            width=10,
            default_val=300,
            side="top",
        )

        dropdowns = []
        for group_num in range(1, int(selected_group) + 1):
            label_text = f"Group {group_num} Color:"
            dropdown_label, dropdown_color = create_dropdown(
                parent=options,
                label_text=label_text,
                options=color_choices,
            )
            dropdown_color.set(color_choices[group_num - 1])
            dropdowns.append((dropdown_label, dropdown_color))

        spm_x_label = create_label_entry(
            parent=options,
            label_text="Plot X Label:",
            width=25,
            default_val="Percent of 'X'",
            side="top",
        )
        group_strings = ["Group 1", "Group 2", "Group 3"]  # Set possible groups names
        default_group_names = ", ".join(
            group_strings[: int(selected_group)]
        )  # Grab group names based on "selected_group"
        group_names = create_label_entry(
            parent=options,
            label_text="Group Names:",
            width=35,
            default_val=default_group_names,
            side="top",
        )

        def get_ylabel(spm_y_box):
            spm_y_box.delete(0, "end")
            result = (
                filedialog.askopenfilename(
                    title="Select Y-Labels Excel File",
                    multiple=False,
                    filetypes=(("Excel Files", "*.xlsx"),),
                ),
            )
            spm_y_box.insert(0, result)

        y_label = ttk.Label(options, text="Y-Label File:")
        y_label.pack(side="top")
        spm_y_box = ttk.Entry(options, width=35, justify="center")
        spm_y_box.pack(side="top")
        y_button = browse_in_button(
            options,
            "Browse",
            lambda: get_ylabel(spm_y_box),
        )

        for widget in entry_frame.winfo_children():
            widget.destroy()

        if selected_group == "1":
            test_options = ["One-sample t test"]
            entry_labels, entry_boxes, entry_buttons = create_entry_in(
                entry_frame, ["Group 1 Data:"]
            )
            output_label, output_box, output_button = create_entry_out(
                entry_frame, ["Output Directory:"]
            )
        elif selected_group == "2":
            test_options = ["Paired t test", "Two-sample t test"]
            entry_labels, entry_boxes, entry_buttons = create_entry_in(
                entry_frame, ["Group 1 Data:", "Group 2 Data:"]
            )
            output_label, output_box, output_button = create_entry_out(
                entry_frame, ["Output Directory:"]
            )
        elif selected_group == "3":
            test_options = [
                "One-way ANOVA",
                "One-way Rep. Meas.",
            ]
            entry_labels, entry_boxes, entry_buttons = create_entry_in(
                entry_frame, ["Group 1 Data:", "Group 2 Data:", "Group 3 Data:"]
            )
            output_label, output_box, output_button = create_entry_out(
                entry_frame, ["Output Directory:"]
            )
        else:
            test_options = ["Select group(s) first!"]
            entry_labels, entry_boxes, entry_buttons = create_entry_in(
                entry_frame, ["Select group(s) first!"]
            )
        execute_function_button(
            entry_frame,
            "Perform Analysis",
            lambda: tf.spm_analysis(
                select_a_test=test_dropdown.get(),
                group_names=group_names.get().split(","),
                selected_group=selected_group,
                g1_in=entry_boxes[0].get(),
                g2_in=entry_boxes[1].get() if len(entry_boxes) > 1 else None,
                g3_in=entry_boxes[2].get() if len(entry_boxes) > 2 else None,
                output_path=output_box[0].get(),
                alpha=alpha.get(),
                equal_var=equal_var.get(),
                two_tail=two_tail.get(),
                dpi=spm_dpi.get(),
                g1_color=dropdowns[0][1].get(),
                g2_color=dropdowns[1][1].get() if len(dropdowns) > 1 else None,
                g3_color=dropdowns[2][1].get() if len(dropdowns) > 2 else None,
                plot_x_label=spm_x_label.get(),
                plot_y_labels=spm_y_box.get(),
            ),
        )

        for button in entry_buttons:
            button.configure(bg="#228B22", cursor="hand2")
        output_button[0].configure(bg="#0047AB", cursor="hand2")
        test_dropdown["values"] = test_options
        test_dropdown.set(test_options[0])

    spm_groups, group_dropdown = create_dropdown(
        dropdown_frame, "Groups:", ["1", "2", "3"]
    )
    group_dropdown.bind("<<ComboboxSelected>>", on_group_selected)
    test_options, test_dropdown = create_dropdown(
        dropdown_frame, "Available Tests:", ["Select group(s) first!"]
    )
    test_dropdown.bind(
        "<<ComboboxSelected>>", lambda event: on_option_selected(event, test_dropdown)
    )


def return_to_main(main_tab):
    if not main_tab.tabs():
        messagebox.showerror("No Tabs Open", "No tabs are currently open.")
        return
    result = messagebox.askyesno(
        "Main Tab", "Do you want to close all tabs?", icon="question"
    )
    if result:
        for tab_id in main_tab.tabs():
            main_tab.forget(tab_id)


def exit_application():
    result = messagebox.askyesno("Exit", "Do you really want to exit?", icon="question")
    if result:
        root.destroy()
        sys.exit()


def restart_program():
    root.destroy()
    python_executable = sys.executable
    subprocess.Popen(
        [
            python_executable,
            "BiomechanicsToolbox.py",
        ]
    )


def check_tab_exists(tab_name):
    for tab_id in main_tab.tabs():
        tab_text = main_tab.tab(tab_id, "text")
        if tab_text == tab_name:
            main_tab.select(tab_id)
            return True


def reset_tab(tab_name):
    reset_items = {
        "Script Gen": open_scriptgen_tab,
        "EMG": open_emg_tab,
        "Batch": open_batch_tab,
        "Normalize": open_normalize_tab,
        "Quality Check": open_quality_check_tab,
        "Event Pick": open_eventpick_tab,
        "Event Compile": open_eventcompile_tab,
        "Ensemble": open_ensemble_tab,
        "SPM": open_spm_tab,
    }
    for tab_id in main_tab.tabs():
        tab_text = main_tab.tab(tab_id, "text")
        if tab_text == tab_name:
            main_tab.forget(tab_id)
            reset_items[tab_name]()
            return


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = (screen_width - width) // 2
    y_coordinate = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


def open_github(event):
    result = messagebox.askokcancel(
        "Open GitHub",
        "This will open a web browser window. Do you want to open the GitHub page for this project?",
    )
    if not result:
        return
    webbrowser.open("https://github.com/WaltMenke/BiomechanicsToolbox")


def open_linkedin(event):
    result = messagebox.askokcancel(
        "Open LinkedIn",
        "This will open a web browser window. Do you want to open my LinkedIn page?",
    )
    if not result:
        return
    webbrowser.open("https://www.linkedin.com/in/walter-menke-172760104/")


##################### Save and Load Parameter Functions ######################
def save_params(tab_name):
    save_functions = {
        "Script Gen": save_scriptgen,
        "EMG": save_emg,
        "Batch": save_batch,
        "Normalize": save_normalize,
        "Quality Check": save_qualitycheck,
        "Event Pick": save_eventpick,
        "Event Compile": save_eventcompile,
        "Ensemble": save_ensemble,
        "SPM": save_spm,
    }
    selected_tab = main_tab.select()
    for tab_id in main_tab.tabs():
        tab_text = main_tab.tab(tab_id, "text")
        if tab_text in save_functions and tab_id == selected_tab:
            save_functions[tab_text]()


def load_params(tab_name):
    load_functions = {
        "Script Gen": load_scriptgen,
        # "EMG": load_emg,
        "Batch": load_batch,
        "Normalize": load_normalize,
        "Quality Check": load_qualitycheck,
        # "Event Pick": load_eventpick,
        # "Event Compile": load_eventcompile,
        "Ensemble": load_ensemble,
        "SPM": load_spm,
    }
    try:
        selected_tab = main_tab.select()
        for tab_id in main_tab.tabs():
            tab_text = main_tab.tab(tab_id, "text")
            if tab_text in load_functions and tab_id == selected_tab:
                load_functions[tab_text]()
    except ttk.TclError:
        messagebox.showerror(
            "Save Failed", "No tabs open. Please open a tab and try again."
        )
        return


def save_scriptgen():
    param_save = filedialog.asksaveasfilename(
        title="Save ScriptGen Tab Parameters",
        initialdir=".",
        initialfile="ScriptGen_Params.txt",
        defaultextension=".txt",
        filetypes=(("TXT Files", "*.txt"),),
    )
    if not param_save:
        return
    with open(param_save, "w") as file:
        file.write(f"Script Template File: {script_entry.get()}\n")
        file.write(f"Model Template File: {model_entry.get()}\n")
        file.write(f"Height-Weight Table: {heightweight_entry.get()}\n")
        file.write(f"Script Output Directory: {script_out_entry.get()}\n")
    messagebox.showinfo("Save Successful", "ScriptGen tab parameters saved!")


def load_scriptgen():
    param_file = filedialog.askopenfilename(
        title="Select Script Tab Parameters",
        filetypes=(("TXT Files", "*.txt"),),
        multiple=False,
    )
    if not param_file:
        return
    entry_mapping = {
        "Script Template File": script_entry,
        "Model Template File": model_entry,
        "Height-Weight Table": heightweight_entry,
        "Script Output Directory": script_out_entry,
    }

    with open(param_file, "r") as file:
        for line in file:
            line = line.strip()
            params = line.split(": ")
            param_name = params[0].strip()
            param_value = params[1].strip()

            if param_name in entry_mapping:
                entry_mapping[param_name].set(param_value)
        messagebox.showinfo("Load Successful", "ScriptGen tab parameters loaded!")


def save_batch():
    param_save = filedialog.asksaveasfilename(
        title="Save Batch Tab Parameters",
        initialdir=".",
        initialfile="Batch_Params.txt",
        defaultextension=".txt",
        filetypes=(("TXT Files", "*.txt"),),
    )
    if not param_save:
        return
    with open(param_save, "w") as file:
        file.write(f"V3D Data Inputs: {batch_in_entry.get()}\n")
        file.write(f"Output Directory: {batch_out_entry.get()}\n")
        file.write(f"Trials per Subject: {batch_trials.get()}\n")
        file.write(f"String to Search: {batch_search_entry.get()}\n")
        file.write(f"File Save Name: {batch_file_savename.get()}\n")
        file.write(f"Components: {batch_components_entry.get()}\n")
        file.write(f"Inputs Normalized: {batch_normalized.get()}\n")
    messagebox.showinfo("Save Successful", "Batch tab parameters saved!")


def load_batch():
    param_file = filedialog.askopenfilename(
        title="Select Batch Tab Parameters",
        filetypes=(("TXT Files", "*.txt"),),
        multiple=False,
    )
    if not param_file:
        return
    entry_mapping = {
        "V3D Data Inputs": batch_in_entry,
        "Output Directory": batch_out_entry,
        "Trials per Subject": batch_trials,
        "String to Search": batch_search_entry,
        "File Save Name": batch_file_savename,
        "Components": batch_components_entry,
        "Inputs Normalized": batch_normalized,
    }
    with open(param_file, "r") as file:
        for line in file:
            line = line.strip()
            params = line.split(": ")
            param_name = params[0].strip()
            param_value = params[1].strip()

            if param_name in entry_mapping:
                entry_mapping[param_name].set(param_value)
    messagebox.showinfo("Load Successful", "Batch tab parameters loaded!")


def save_normalize():
    param_save = filedialog.asksaveasfilename(
        title="Save Normalize Tab Parameters",
        initialdir=".",
        initialfile="Normalize_Params.txt",
        defaultextension=".txt",
        filetypes=(("TXT Files", "*.txt"),),
    )
    if not param_save:
        return
    with open(param_save, "w") as file:
        file.write(f"Batched Data File: {norm_in.get()}\n")
        file.write(f"Output Directory: {norm_out.get()}\n")
    messagebox.showinfo("Save Successful", "Normalize tab parameters saved!")


def load_normalize():
    param_file = filedialog.askopenfilename(
        title="Select Normalize Tab Parameters",
        filetypes=(("TXT Files", "*.txt"),),
        multiple=False,
    )
    if not param_file:
        return
    entry_mapping = {"Batched Data File": norm_in, "Output Directory": norm_out}
    with open(param_file, "r") as file:
        for line in file:
            line = line.strip()
            params = line.split(": ")
            param_name = params[0].strip()
            param_value = params[1].strip()

            if param_name in entry_mapping:
                entry_mapping[param_name].set(param_value)
    messagebox.showinfo("Load Successful", "Normalize tab parameters loaded!")


def save_qualitycheck():
    param_save = filedialog.asksaveasfilename(
        title="Save Quality Check Tab Parameters",
        initialdir=".",
        initialfile="QualityCheck_Params.txt",
        defaultextension=".txt",
        filetypes=(("TXT Files", "*.txt"),),
    )
    if not param_save:
        return
    with open(param_save, "w") as file:
        file.write(f"Batched Data Input Directory: {qual_in.get()}\n")
        file.write(f"Subject Numbers: {qual_subs.get()}\n")
    messagebox.showinfo("Save Successful", "Quality Check parameters saved!")


def load_qualitycheck():
    param_file = filedialog.askopenfilename(
        title="Select Quality Check Tab Parameters",
        filetypes=(("TXT Files", "*.txt"),),
        multiple=False,
    )
    if not param_file:
        return
    entry_mapping = {
        "Batched Data Input Directory": qual_in,
        "Subject Numbers": qual_subs,
    }
    with open(param_file, "r") as file:
        for line in file:
            line = line.strip()
            params = line.split(": ")
            param_name = params[0].strip()
            param_value = params[1].strip()

            if param_name in entry_mapping:
                entry_mapping[param_name].set(param_value)
    messagebox.showinfo("Load Successful", "Quality Check parameters loaded!")


def save_ensemble():
    param_save = filedialog.asksaveasfilename(
        title="Save Ensemble Tab Parameters",
        initialdir=".",
        initialfile="Ensemble_Params.txt",
        defaultextension=".txt",
        filetypes=(("TXT Files", "*.txt"),),
    )
    if not param_save:
        return
    with open(param_save, "w") as file:
        file.write(f"Normalized Data File: {ensemble_in.get()}\n")
        file.write(f"Output Directory: {ensemble_out.get()}\n")
        file.write(f"Detected Variables: {ens_variables_listbox.get(0,'end')}\n")
        file.write(f"Axes Titles: {ens_axes_listbox.get(0,'end')}\n")
        file.write(f"TIFF DPI: {ensemble_dpi.get()}\n")
        file.write(f"Mean Color: {ens_mean_color.get()}\n")
        file.write(f"Std Color: {ens_std_color.get()}\n")
        file.write(f"Y Line at 0?: {y_line_var.get()}\n")
        pass


def load_ensemble():
    param_file = filedialog.askopenfilename(
        title="Select Ensemble Tab Parameters",
        filetypes=(("TXT Files", "*.txt"),),
        multiple=False,
    )
    if not param_file:
        return
    entry_mapping = {
        "Normalized Data File": ensemble_in,
        "Output Directory": ensemble_out,
        "Detected Variables": ens_variables_listbox,
        "Axes Titles": ens_axes_listbox,
        "TIFF DPI": ensemble_dpi,
        "Mean Color": ens_mean_color,
        "Std Color": ens_std_color,
        "Y Line at 0?": y_line_var,
    }
    with open(param_file, "r") as file:
        for line in file:
            line = line.strip()
            params = line.split(": ")
            param_name = params[0].strip()
            param_value = params[1].strip()
            print("param_name:", param_name)

            if param_name == "Detected Variables":
                print("Worked for vars")
                entries = ast.literal_eval(param_value)
                ens_variables_listbox.delete(0, "end")
                for entry in entries:
                    ens_variables_listbox.insert("end", entry)
            elif param_name == "Axes Titles":
                print("Worked for axes")
                entries = ast.literal_eval(param_value)
                ens_axes_listbox.delete(0, "end")
                for entry in entries:
                    ens_axes_listbox.insert("end", entry)

            elif param_name in entry_mapping:
                entry_mapping[param_name].set(param_value)
    messagebox.showinfo("Load Successful", "Ensemble parameters loaded!")


def save_spm():
    try:
        alpha.get()
    except NameError:
        messagebox.showerror(
            "Error", "Select the appropriate group number before saving SPM parameters!"
        )
        return
    param_save = filedialog.asksaveasfilename(
        title="Save SPM Tab Parameters",
        initialdir=".",
        initialfile="SPM_Params.txt",
        defaultextension=".txt",
        filetypes=(("TXT Files", "*.txt"),),
    )
    if not param_save:
        return
    with open(param_save, "w") as file:
        file.write(f"Groups: {group_dropdown.get()}\n")
        file.write(f"Available Tests: {test_dropdown.get()}\n")
        file.write(f"Group 1 Data: {entry_boxes[0].get()}\n")
        file.write(f"Group 2 Data: {entry_boxes[1].get()}\n") if len(
            entry_boxes
        ) > 1 else None
        file.write(f"Group 3 Data: {entry_boxes[2].get()}\n") if len(
            entry_boxes
        ) > 2 else None
        file.write(f"Output Directory: {output_box[0].get()}\n")
        file.write(f"Alpha: {alpha.get()}\n")
        file.write(f"Equal Var: {equal_var.get()}\n")
        file.write(f"Two Tail: {two_tail.get()}\n")
        file.write(f"TIFF DPI: {spm_dpi.get()}\n")
        file.write(f"Group 1 Color: {dropdowns[0][1].get()}\n")
        file.write(f"Group 2 Color: {dropdowns[1][1].get()}\n") if len(
            dropdowns
        ) > 1 else None
        file.write(f"Group 3 Color: {dropdowns[2][1].get()}\n") if len(
            dropdowns
        ) > 2 else None
        file.write(f"Plot X Label: {spm_x_label.get()}\n")
        file.write(f"Group Names: {group_names.get()}\n")
        file.write(f"Plot Y Labels: {spm_y_box.get()}")
    messagebox.showinfo("Save Successful", "SPM tab parameters saved!")


def load_spm():
    try:
        alpha.get()
    except NameError:
        messagebox.showerror(
            "Error",
            "Select the appropriate group number before loading SPM parameters!",
        )
        return
    param_file = filedialog.askopenfilename(
        title="Select SPM Tab Parameters",
        filetypes=(("TXT Files", "*.txt"),),
        multiple=False,
    )
    if not param_file:
        return
    entry_mapping = {
        "Groups": group_dropdown,
        "Available Tests": test_dropdown,
        "Group 1 Data": tk.StringVar(),
        "Group 2 Data": tk.StringVar() if len(entry_boxes) > 1 else None,
        "Group 3 Data": tk.StringVar() if len(entry_boxes) > 2 else None,
        "Output Directory": tk.StringVar(),
        "Alpha": alpha,
        "Equal Var": equal_var,
        "Two Tail": two_tail,
        "TIFF DPI": spm_dpi,
        "Group 1 Color": tk.StringVar(),
        "Group 2 Color": tk.StringVar() if len(dropdowns) > 1 else None,
        "Group 3 Color": tk.StringVar() if len(dropdowns) > 2 else None,
        "Plot X Label": spm_x_label,
        "Group Names": group_names,
        "Plot Y Labels": tk.StringVar(),
    }

    with open(param_file, "r") as file:
        for line in file:
            line = line.strip()
            params = line.split(": ")
            param_name = params[0].strip()
            param_value = params[1].strip()

            if param_name in entry_mapping:
                index_str = re.search(r"\d+", param_name)
                if index_str:
                    index = int(index_str.group()) - 1

                    if "Data" in param_name:
                        try:
                            entry_boxes[index].delete(0, tk.END)
                            entry_boxes[index].insert(0, param_value)
                        except IndexError:
                            messagebox.showerror(
                                "Error",
                                "Group selected was fewer than specified in the parameters! Re-select group and try again.",
                            )
                            return
                    elif "Color" in param_name:
                        dropdowns[index][1].delete(0, tk.END)
                        dropdowns[index][1].insert(0, param_value)
                elif "Output" in param_name:
                    output_box[0].delete(0, tk.END)
                    output_box[0].insert(0, param_value)
                elif "Y Labels" in param_name:
                    spm_y_box.delete(0, tk.END)
                    spm_y_box.insert(0, param_value)
                else:
                    entry_mapping[param_name].set(param_value)
    if index_str != selected_group:
        messagebox.showerror(
            "Error",
            "Group selected was larger than specified in the parameters! Re-select group and try again.",
        )
        return
    messagebox.showinfo("Load Successful", "SPM tab parameters loaded!")


def handle_save_params():
    try:
        save_params(main_tab.tab(main_tab.select(), "text"))
    except Exception:
        messagebox.showerror(
            "Save Failed",
            "Cannot save tab parameters without a tab open. Please open a tab and try again.",
        )


def handle_load_params():
    try:
        load_params(main_tab.tab(main_tab.select(), "text"))
    except Exception as e:
        messagebox.showerror(
            "Load Failed",
            "Cannot load tab parameters without a tab open. Please open a tab and try again.",
        )


##################### Main Menu Creation ######################
root = ttk.Window()
root.title("Biomechanics Toolbox")
root.pack_propagate(0)
main_tab = ttk.Notebook(root)
main_tab.pack(fill="both", expand=True)

center_window(root, 750, 800)
root.iconbitmap("BT_Icon.ico")
root.iconbitmap(default="BT_Icon.ico")


def add_menu_items(menu, items):
    for label, command in items.items():
        menu.add_command(label=label, command=command)


def close_current_tab():
    if not main_tab.tabs():
        messagebox.showerror("No Tabs Open", "No tabs are currently open.")
        return
    main_tab.forget(main_tab.select())


file_menu_items = {
    "Reset Tab Entries": lambda: reset_tab(main_tab.tab(main_tab.select(), "text")),
    "Close Current Tab": lambda: close_current_tab(),
    "Close All Tabs": lambda: return_to_main(main_tab),
    "Restart": restart_program,
    "Exit": exit_application,
}

parameter_menu_items = {
    "Save Tab Params": lambda: handle_save_params(),
    "Load Tab Params": lambda: handle_load_params(),
}


functions_menu_items = {
    "Script Gen": open_scriptgen_tab,
    "EMG": open_emg_tab,
    "Batch": open_batch_tab,
    "Normalize": open_normalize_tab,
    "Quality Check": open_quality_check_tab,
    "Event Pick": open_eventpick_tab,
    "Event Compile": open_eventcompile_tab,
    "Ensemble": open_ensemble_tab,
    "SPM": open_spm_tab,
}

help_menu_items = {"Toolbox Documentation": open_program_docs}

menubar = ttk.Menu(master=root)
menus = {
    "Options": file_menu_items,
    "Parameters": parameter_menu_items,
    "Functions": functions_menu_items,
    "Help": help_menu_items,
}

for menu_label, menu_items in menus.items():
    menu = ttk.Menu(menubar)
    add_menu_items(menu, menu_items)
    menubar.add_cascade(label=menu_label, menu=menu)
root.config(menu=menubar)

label_configurations = [
    ("Biomechanics Toolbox", ("Helvetica", 14, "bold"), "#A52A2A", 35),
    (
        "  This program was developed to facilitate a more efficient workflow for\n\tbiomechanics data processing and presentation.",
        ("Helvetica", 10),
        None,
        5,
    ),
    (
        "    1. V3D Script and Model Generation\n    2. EMG Processing\n    3. Batch Processing\n    4. Normalization\n    5. Data Quality Checks\n    6. Event Picking\n    7. Event Compiling\n    8. Ensemble Curves\n    9. SPM Analysis",
        ("Helvetica", 10),
        None,
        5,
    ),
    (
        "    This program requires the following packages to be installed:\n\n\t - matplotlib\t - numpy\t\t - os\n\t - pandas\t\t - re\t\t - subprocess\n\t - sys\t\t - tkinter\t\t - ttkbootstrap\n\t - spm1d\t\t - webbrowser\t - openpyxl\n\n    A full list of required packages and their versions can be found\n\t in the documentation (ToolboxRequirements.txt)",
        ("Helvetica", 10),
        None,
        5,
    ),
]

for text, font, foreground, pady in label_configurations:
    label = ttk.Label(main_tab, text=text, font=font, foreground=foreground)
    label.pack(padx=5, pady=pady, anchor="n")

linkedin_label = tk.Label(
    main_tab,
    text="Contact me on LinkedIn",
    font=("Helvetica", 10, "underline"),
    cursor="hand2",
)
linkedin_label.pack(side="bottom", pady=2)
linkedin_label.bind("<Button-1>", open_linkedin)

github_label = tk.Label(
    main_tab,
    text="Check out this project on GitHub",
    font=("Helvetica", 10, "underline"),
    cursor="hand2",
)
github_label.pack(side="bottom", pady=2)
github_label.bind("<Button-1>", open_github)


author_label = ttk.Label(
    root,
    text="\t\t      © Copyright 2023, Walter Menke\nCreated in Python v3.11.6 (64-bit) on Windows 11 in Visual Studio Code v1.84.2.",
    font=("Helvetica", 8),
)
author_label.pack(padx=5, pady=2, anchor="s")

root.mainloop()
