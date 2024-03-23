import numpy as np
import pandas as pd
import os
import re
import csv
import ast
import sys
from openpyxl import Workbook
from collections import OrderedDict
import tkinter as tk
from tkinter import ttk, filedialog, PhotoImage, messagebox, simpledialog
import ttkbootstrap as ttk


def list_csv_files(directory):
    csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]
    return csv_files


def extract_subject_number(file_name):
    return file_name.split("_")[0][1:]  # Extracts the number after 'S'


def extract_condition_number(file_name):
    return file_name.split("_")[1][1:]  # Extracts the number after 'C'


def replace_nan(value):
    if np.isnan(value):
        return "NaN"
    else:
        return value


def generate_value_rows(variable_names):
    value_rows = []
    variable_count = len(variable_names)
    for _ in range(3):  # Repeat the cycle 3 times
        for variable in variable_names:
            for event in events:
                value_rows.append([variable, "Value", event])
    return value_rows[: variable_count * 3]  # Limit to 3 rows per variable


# Function to generate row names for Index
def generate_index_rows(variable_names):
    index_rows = []
    variable_count = len(variable_names)
    for _ in range(3):  # Repeat the cycle 3 times
        for variable in variable_names:
            for event in events:
                index_rows.append([variable, "Index", event])
    return index_rows[: variable_count * 3]  # Limit to 3 rows per variable


def generate_per_loc_rows(variable_names):
    per_loc_rows = []
    variable_count = len(variable_names)
    for _ in range(3):  # Repeat the cycle 3 times
        for variable in variable_names:
            for event in events:
                per_loc_rows.append([variable, "Per_Loc", event])
    return per_loc_rows[: variable_count * 3]  # Limit to 3 rows per variable


# Subprocess inputs from main window
root = ttk.Window()
root.withdraw()
root.iconbitmap("BT_Icon.ico")
root.iconbitmap(default="BT_Icon.ico")

compile_in = sys.argv[1]
compile_out = sys.argv[2]

result = messagebox.askyesno(
    "Compile",
    "Before compiling, are you sure the input directory only contains properly named CSV Event Output files?",
    icon="question",
)
if not result:
    messagebox.showinfo("Compile Canceled", "Compile operation canceled.")
    sys.exit()

num_entries = None

maxima_stats_by_condition = {}
minima_stats_by_condition = {}

reorg_max = {}
reorg_min = {}

maxima_averages = {}
maxima_std_devs = {}
minima_averages = {}
minima_std_devs = {}

events = ["Event 1", "Event 2", "Event 3"]

headers = [
    "SUBJECT",
    "VARIABLE",
    "TYPE",
    "NUMBER",
    "Maxima Averages",
    "Maxima Standard Deviations",
    "Minima Averages",
    "Minima Standard Deviations",
]

pattern = r"^S\d{1,2}_C\d{1,2}_(Maxima|Minima)\.csv$"  # Ensures naming structure is like 'S1_C1_Maxima.csv'
relevant_files = list_csv_files(compile_in)
for file_name in relevant_files:
    if not re.match(pattern, file_name):
        print("Error: File", file_name, "does not match the required naming structure.")
        break
else:
    pass

ref_file = relevant_files[0]
cond_ref = ref_file.split("_")[1][1:]  # Extracts the number after _C

present_conditions = [cond_ref]
for file in relevant_files:
    current_cond = file.split("_")[1][1:]
    if cond_ref != current_cond and current_cond not in present_conditions:
        present_conditions.append(current_cond)

sub_count = []
for file in relevant_files:
    subject = extract_subject_number(file)
    if subject not in sub_count:
        sub_count.append(subject)
files_by_condition = {cond: [] for cond in present_conditions}


for file in relevant_files:  # Splits up files by Condition number
    condition_number = extract_condition_number(file)
    files_by_condition[condition_number].append(file)


for condition, files in files_by_condition.items():
    if num_entries is None:
        num_entries = len(files)
    else:
        if len(files) != num_entries:
            messagebox.showerror(
                "Warning",
                f"Number of entries in condition {condition} differs from others. Check the file inputs in {compile_in} and try again.",
            )
            break
else:
    pass

for condition, files in files_by_condition.items():
    maxima_count = sum(1 for file in files if "Maxima" in file)
    minima_count = sum(1 for file in files if "Minima" in file)
    if maxima_count != minima_count:
        messagebox.showerror(
            "Warning",
            f"Number of 'Maxima' files does not match number of 'Minima' files in condition {condition}. Check the file inputs in {compile_in} and try again.",
        )
        break
    else:
        pass
for condition, files in files_by_condition.items():
    reference_third_line = None
    for file_name in files:
        file_path = os.path.join(compile_in, file_name)
        prefix = file_name.split(".")[
            0
        ]  # Extract everything before .csv in the filename
        with open(file_path, "r", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            first_line_str = "".join(prefix)  # Convert the list to a string
            prefix_without_extension = prefix.split(".")[0]  # Remove the file extension
            if not first_line_str == prefix_without_extension:
                messagebox.showerror(
                    "Warning",
                    f"File {file_name} does not match expected naming structure. Check the file inputs in {compile_in} and try again.",
                )
                break
            else:
                next(csv_reader)  # Skip the first line
                next(csv_reader)  # Skip the second line
                third_line = next(csv_reader)
                if reference_third_line is None:
                    ref_file = file_name
                    reference_third_line = third_line
                else:
                    if third_line != reference_third_line:
                        messagebox.showerror(
                            "Warning",
                            f"Third line of data in file {file_name} relative to expected from {ref_file}. Check the file inputs in {compile_in} and try again.",
                        )
                        break
lists = [ast.literal_eval(entry) for entry in reference_third_line if entry]
flat_entries = [item for sublist in lists for item in sublist]
variable_names = list(
    OrderedDict.fromkeys(flat_entries)
)  # Maintains order of variable names

for condition, files in files_by_condition.items():
    maxima_stats = []
    minima_stats = []

    for file_name in files:
        file_path = os.path.join(compile_in, file_name)
        file_type = "Maxima" if "Maxima" in file_name else "Minima"

        with open(file_path, "r", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)

            for row in csv_reader:
                try:
                    row = [float(value) if value != "nan" else np.nan for value in row]

                    if not any(np.isnan(row)):
                        row_avg = np.nanmean(row)
                        row_std = np.nanstd(row)
                    else:
                        row_avg = np.nan
                        row_std = np.nan

                    if file_type == "Maxima":
                        maxima_stats.append((row_avg, row_std))
                    else:
                        minima_stats.append((row_avg, row_std))
                except ValueError:  # Catches non-numeric rows
                    continue

    maxima_stats_by_condition[condition] = maxima_stats
    minima_stats_by_condition[condition] = minima_stats

for condition, maxima_stats in maxima_stats_by_condition.items():
    minima_stats = minima_stats_by_condition[condition]

    reorg_max[condition] = []
    reorg_min[condition] = []

    for i in range(9):
        for subject in range(len(sub_count)):
            start_index = (subject * len(variable_names) * 9) + (
                i * len(variable_names)
            )

            selected_maxima_rows = maxima_stats[
                start_index : start_index + len(variable_names)
            ]
            selected_minima_rows = minima_stats[
                start_index : start_index + len(variable_names)
            ]

            reorg_max[condition].extend(selected_maxima_rows)
            reorg_min[condition].extend(selected_minima_rows)

workbook = Workbook()

for condition, max_data in reorg_max.items():
    sheet = workbook.create_sheet(title="C" + str(condition))

    sheet.append(headers)
    num_subjects = len(sub_count)
    num_variables = len(variable_names)
    num_events = 3

    for number_counter in range(1, num_events + 1):
        for subject_idx, subject in enumerate(sub_count):
            for variable_idx, variable in enumerate(variable_names):
                for event in range(1, num_events + 1):
                    # Write subject, variable, type, number
                    if number_counter == 1:
                        sheet.append(
                            [
                                sub_count[subject_idx],
                                variable,
                                "Value",
                                f"Event {event}",
                            ]
                        )
                    elif number_counter == 2:
                        sheet.append(
                            [
                                sub_count[subject_idx],
                                variable,
                                "Value",
                                f"Event {event}",
                            ]
                        )
                    elif number_counter == 3:
                        sheet.append(
                            [
                                sub_count[subject_idx],
                                variable,
                                "Value",
                                f"Event {event}",
                            ]
                        )

    for i, row in enumerate(
        sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=1, max_col=4), start=1
    ):
        subject_idx = (i - 1) // num_variables % num_subjects
        variable_idx = (i - 1) // (num_events * 3) % num_variables
        # Update SUBJECT column (iterate every 3 rows)
        row[0].value = sub_count[subject_idx]

        # Update VARIABLE column
        row[1].value = variable_names[variable_idx]

        # Update TYPE column
        type_value_index = (i - 1) // (num_events * num_subjects * num_variables)
        type_value = ["Value", "Index", "Per_Loc"][type_value_index]
        row[2].value = type_value

        # Update NUMBER column
        row[3].value = f"Event {(i - 1) % num_events + 1}"

    # Write maxima data
    for i, max_row in enumerate(max_data, start=2):  # Start from the correct row index
        for j, value in enumerate(max_row, start=5):
            sheet.cell(row=i, column=j).value = replace_nan(value)

    # Write minima data
    min_data = reorg_min[condition]
    for i, min_row in enumerate(min_data, start=2):  # Start from the correct row index
        for j, value in enumerate(
            min_row, start=7
        ):  # Starting from column 9 for minima
            sheet.cell(row=i, column=j).value = replace_nan(value)
# Remove the default sheet created by openpyxl
workbook.remove(workbook.active)
savepath = filedialog.asksaveasfilename(
    defaultextension=".xlsx",
    filetypes=[("Excel files", "*.xlsx")],
    initialfile="Events_By_Subject.xlsx",
)
if savepath:
    workbook.save(filename=savepath)
else:
    messagebox.showinfo("Save Error", "Save operation canceled by user.")
workbook.close()


for matrix, avg_list, std_dev_list in [
    (reorg_max, maxima_averages, maxima_std_devs),
    (reorg_min, minima_averages, minima_std_devs),
]:
    for condition, rows in matrix.items():
        avg_list[condition] = []
        std_dev_list[condition] = []

        for chunk in range(len(rows) // (len(variable_names) * len(sub_count))):
            for row_set in range(3):
                avg_values = []

                for subject in range(len(sub_count)):
                    start_index = (
                        chunk * (len(variable_names) * len(sub_count)) + subject * 3
                    )

                    selected_row = rows[start_index + row_set]

                    avg_value = selected_row[0]
                    if not np.isnan(avg_value):
                        avg_values.append(avg_value)

                if avg_values:  # Check if avg_values is not empty
                    row_avg = np.nanmean(avg_values)
                    row_std = np.nanstd(avg_values)

                    avg_list[condition].append(row_avg)
                    std_dev_list[condition].append(row_std)
                else:
                    # Handle case when avg_values is empty
                    avg_list[condition].append(np.nan)
                    std_dev_list[condition].append(np.nan)

workbook = Workbook()
for condition, _ in maxima_averages.items():
    # Create a new sheet for the condition
    sheet = workbook.create_sheet(title="C" + str(condition))

    # Write row names as headers
    variable_names = sorted(variable_names)  # Ensure alphabetical order
    value_rows = generate_value_rows(variable_names)
    index_rows = generate_index_rows(variable_names)
    per_loc_rows = generate_per_loc_rows(variable_names)
    all_rows = value_rows + index_rows + per_loc_rows
    for i, row_name in enumerate(all_rows, start=2):  # Start from row 2
        sheet.cell(row=i, column=1).value = row_name[0]
        sheet.cell(row=i, column=2).value = row_name[1]
        sheet.cell(row=i, column=3).value = row_name[2]

        # Write headers for data
    sheet.cell(row=1, column=1).value = "VARIABLE"
    sheet.cell(row=1, column=2).value = "TYPE"
    sheet.cell(row=1, column=3).value = "NUMBER"
    sheet.cell(row=1, column=4).value = "Maxima Averages"
    sheet.cell(row=1, column=5).value = "Maxima Standard Deviations"
    sheet.cell(row=1, column=6).value = "Minima Averages"
    sheet.cell(row=1, column=7).value = "Minima Standard Deviations"

    # Write data
    for i in range(len(maxima_averages[condition])):
        max_avg = replace_nan(maxima_averages[condition][i])
        max_std = replace_nan(maxima_std_devs[condition][i])
        min_avg = replace_nan(minima_averages[condition][i])
        min_std = replace_nan(minima_std_devs[condition][i])
        sheet.cell(row=i + 2, column=4).value = max_avg
        sheet.cell(row=i + 2, column=5).value = max_std
        sheet.cell(row=i + 2, column=6).value = min_avg
        sheet.cell(row=i + 2, column=7).value = min_std

workbook.remove(workbook.active)
savepath = filedialog.asksaveasfilename(
    defaultextension=".xlsx",
    filetypes=[("Excel files", "*.xlsx")],
    initialfile="Events_Synthesized.xlsx",
)
if savepath:
    workbook.save(filename=savepath)
else:
    messagebox.showinfo("Save Error", "Save operation canceled by user.")
workbook.close()
messagebox.showinfo(
    "Save Successful",
    f"Events successfully compiled. Returning to the Biomechanics Toolbox...",
)
