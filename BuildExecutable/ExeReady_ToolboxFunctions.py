import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, PhotoImage, messagebox, simpledialog
import ttkbootstrap as ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import re
import numpy.typing as npt
import spm1d

try:
    import scienceplots
except Exception as e:
    print(f"Caught an exception: {e}")
    # messagebox.showinfo(
    #     "Error",
    #     "SciencePlots not installed. https://github.com/garrettj403/SciencePlots",
    # )
    pass


def get_vars(
    filename: str,
    unique: int = 0,
    trial_num: int = 5,
    X: bool = 1,
    Y: bool = 1,
    Z: bool = 1,
) -> str:
    """This function imports a user-specified V3D output file (full path) and returns a list of the variable names.

    INPUTS:
        filename: FULL path to directory of V3D output file
        unique (optional): Whether the variable output strings should be replicated (in case of multiple components)
        trial_num (optional): Number of trials (default is 5)
        X (optional): Indicates if the X component was exported for all variables (default is 1)
        Y (optional): Indicates if the Y component was exported for all variables (default is 1)
        Z (optional): Indicates if the Z component was exported for all variables (default is 1)

    OUTPUTS:
        List of strings containing variable names

    DEPENDENCIES:
        Pandas, OS

    SEE ALSO:
        None

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    if sum([X, Y, Z]) < 1:
        raise ValueError(
            "At least one component must be exported. X, Y, and/or Z must be 1."
        )
    if unique != 0 and unique != 1:
        raise ValueError("Unique must be 0 (false) or 1 (true).")
    if int(trial_num) <= 0:
        raise ValueError("Trial_num must be greater than 0.")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file '{filename}' does not exist.")
    directory_path = os.path.dirname(filename)
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise FileNotFoundError(f"The directory '{directory_path}' does not exist.")

    file = pd.read_csv(
        filename, sep="\t", header=None
    )  # Reads in variable names from V3D output file
    var_num = int(
        (len(file.columns) - 1) / int(trial_num)
    )  # Calculates number of variables
    var_num_trim = file.iloc[1, 1 : var_num + 1]  # Drop off first column (frame number)
    if unique == 0:  # If user does not want unique variable names
        var_series = var_num_trim
    else:
        var_series = var_num_trim[1 :: (X + Y + Z)]
    variables = var_series.astype(str).tolist()
    variable_string = ", ".join(variables)
    return variable_string


def trim_header(filename: str) -> npt.NDArray:
    """This function imports a user-specified V3D output file (full path) and trims the headers, removes
    the first column, and converts the remaining columns to float.

    INPUTS:
        filename: FULL path to V3D output file

    OUTPUTS:
        2D numpy array: 2D array of trimmed data

    DEPENDENCIES:
        Numpy, OS

    SEE ALSO:
        None

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    if not os.path.exists(filename):
        raise ValueError(f"{filename} does not exist.")

    file = np.genfromtxt(
        filename,
        delimiter="\t",
        skip_header=5,
        dtype=float,
    )
    file = file[:, 1:]
    return file


def generate_scripts(
    script_template_path: str,
    model_template_path: str,
    heightweight_file: str,
    output_path: str,
) -> None:
    """This function imports a user-specified V3D pipeline file (.v3s), V3D model file (.mdh), and Height-Weight file (.xlsx) and generates a script and model for each subject in the Height-Weight file.

    INPUTS:
        script_file: FULL path to directory of V3D pipeline file (.v3s)
        subject_vec: Vector of subject numbers e.g [4, 6, 7, 9] - this MUST include the template script subject
        condition_vec: Vector of condition numbers e.g [1, 2, 3, 4] - this MUST include the template script condition
        output_dir: FULL path to desired directory to save scripts
        sub_folders (optional): Indicates whether to create a sub-folder for each subject's scripts (default is 0)

    OUTPUTS:
        Multiple script and model files in user-specified directory, corresponding to each subject in the Height-Weight file

    DEPENDENCIES:
        OS, sys, tkinter, ttkbootstrap

    SEE ALSO:
        None

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    try:
        if not os.path.exists(script_template_path):
            raise FileNotFoundError(f"{script_template_path} does not exist.")
        if not os.path.exists(model_template_path):
            raise FileNotFoundError(f"{model_template_path} does not exist.")
        if not os.path.exists(heightweight_file):
            raise FileNotFoundError(f"{heightweight_file} does not exist.")
        if not os.path.exists(output_path):
            messagebox.showinfo(
                "Output Directory",
                "Output directory does not exist. Creating directory.",
            )
            os.mkdir(output_path)

        script_template = pd.read_csv(script_template_path, sep="\t", header=None)

        height_weight = pd.read_excel(heightweight_file)
        for column_name in ["Subject", "Mass", "Height"]:
            if column_name not in height_weight.columns:
                raise ValueError(f"{column_name} column not found in script template.")

        nan_check = height_weight[["Subject", "Mass", "Height"]].isna().any().any()
        if nan_check:
            user_response = messagebox.askyesno(
                "Warning",
                "NaN values are present, indicating inconsistent column lengths in the Height-Weight table. Do you want to continue?",
            )
            if not user_response:
                raise ValueError(
                    "Operation aborted. Please check the Height-Weight to ensure each subject has a corresponding height and mass."
                )

        replace_dict = {
            column: height_weight[column].tolist() for column in height_weight.columns
        }

        model_template = pd.read_csv(model_template_path, sep="\t", header=None)
        subject_vec = replace_dict["Subject"]
        if subject_vec is None or subject_vec == []:
            raise ValueError("Subject column not found in script template.")

        for j in range(0, len(subject_vec)):
            new_script = script_template.copy()

            for i in range(len(new_script) - 1):
                current_row = new_script.at[i, 0]

                if re.search(r"S1", current_row):
                    new_script.at[i, 0] = re.sub(
                        r"S1", f"S{subject_vec[j]}", current_row
                    )
            output_script_path = os.path.join(
                output_path, "Scripts", f"S{subject_vec[j]}.v3s"
            )
            os.makedirs(os.path.dirname(output_script_path), exist_ok=True)
            new_script.to_csv(output_script_path, sep="\t", header=None, index=False)

        for iteration, (subject, mass_replace_value, height_replace_value) in enumerate(
            zip(replace_dict["Subject"], replace_dict["Mass"], replace_dict["Height"]),
            1,
        ):
            new_model = model_template.copy()

            mass_replaced = False
            height_replaced = False

            for i in range(len(new_model) - 1):
                current_row = new_model.at[i, 0]
                next_row = new_model.at[i + 1, 0]

                if (
                    not mass_replaced
                    and re.search(r"/METRIC_NAME=Mass", current_row)
                    and re.search(r"/METRIC_VALUE=", next_row)
                ):
                    new_model.at[i + 1, 0] = re.sub(
                        r"/METRIC_VALUE=\d+(\.\d+)?",
                        f"/METRIC_VALUE={mass_replace_value}",
                        next_row,
                    )
                    mass_replaced = True

                elif (
                    not height_replaced
                    and re.search(r"/METRIC_NAME=Height", current_row)
                    and re.search(r"/METRIC_VALUE=", next_row)
                ):
                    new_model.at[i + 1, 0] = re.sub(
                        r"/METRIC_VALUE=\d+(\.\d+)?",
                        f"/METRIC_VALUE={height_replace_value}",
                        next_row,
                    )
                    height_replaced = True

                if mass_replaced and height_replaced:
                    break

            output_model_path = os.path.join(output_path, "Models", f"S{subject}.mdh")
            os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
            new_model.to_csv(output_model_path, sep="\t", header=None, index=False)
        messagebox.showinfo(
            "Generated Scripts",
            f"Scripts and Models have been generated here: {output_path}",
        )
    except FileNotFoundError as e:
        tk.messagebox.showerror("File Not Found", str(e))
        return
    except ValueError as e:
        tk.messagebox.showerror("Value Error", str(e))
        return


def batch(
    input_directory: str,
    search_query: str,
    output_directory: str,
    file_savename: str,
    trial_num: int = 5,
    X: bool = 1,
    Y: bool = 1,
    Z: bool = 1,
    normalized: bool = 0,
) -> None:
    """This function imports user-specified V3D output files from a directory and returns a flattened numpy array containing all rows, columns, and subjects.

    INPUTS:
        input_directory: FULL path to directory of V3D output .txt files
        search_query: String to search for in V3D output files such as "walk.txt" or regular expression type search such as "L.*4.txt"
        output_directory: FULL path to desired directory to save output .txt file
        file_savename: Name of output .txt file
        trial_num (optional): Number of trials, default is 5 (default is 5)
        X (optional): Indicates if the X component was exported for all variables (default is 1)
        Y (optional): Indicates if the Y component was exported for all variables (default is 1)
        Z (optional): Indicates if the Z component was exported for all variables (default is 1)
        normalized: Indicates if the data inputs are normalized (default is 0)

    OUTPUTS:
        numpy array: Returns a flattened array with shape metadata to return the original shape

    DEPENDENCIES:
        Numpy, OS, re, tkinter

    SEE ALSO:
        batch_reshape
        normalize
        quality_check

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    try:
        if not os.path.exists(input_directory):
            raise FileNotFoundError(
                f"Input directory '{input_directory}' does not exist."
            )
        if not os.path.exists(output_directory):
            raise FileNotFoundError(
                f"Output directory '{output_directory}' does not exist."
            )
        if not os.path.isdir(input_directory):
            raise NotADirectoryError(
                f"Input directory: '{input_directory}' is not a directory."
            )
        if not os.path.isdir(output_directory):
            raise NotADirectoryError(
                f"Output directory: '{output_directory}' is not a directory."
            )
        if normalized != 1 & normalized != 0:
            raise ValueError("Input normalized must be 0 (false) or 1 (true)")
        if int(trial_num) < 1:
            raise ValueError(
                "Input 'Trials per Subject' must be a positive integer of at least 1."
            )
        if not isinstance(search_query, str):
            raise TypeError(
                "'String to Search' must be a string common to all desired files. Such as 'walk.txt'"
            )
        if search_query == "":
            raise ValueError("'String to Search' cannot be empty.")
        if file_savename == "":
            raise ValueError("'File Save Name' cannot be empty.")
        if file_savename.endswith(".txt"):
            raise ValueError("'File Save Name' should not include file extension.")
        file_savename = file_savename + ".txt"

        def check_columns(file_path):
            with open(file_path, "r") as file:
                # Assuming columns are separated by some delimiter, e.g., tab or comma
                first_line = file.readline().strip()
                columns = len(
                    first_line.split("\t")
                )  # Change '\t' to ',' if using comma-separated values

                for line in file:
                    if len(line.strip().split("\t")) != columns:
                        raise ValueError(
                            f"Inconsistent number of columns in file: {file_path}"
                        )
                    return ValueError

        pattern = re.compile(
            f"{search_query}"
        )  # Compiles regular expression string for search
        file_list = [
            f for f in os.listdir(input_directory) if pattern.search(f)
        ]  # Collects all files with specified suffix
        for filename in file_list:
            file_path = os.path.join(input_directory, filename)
            check_columns(file_path)

        row_check, col_check = None, None
        var_list = get_vars(
            os.path.join(input_directory, file_list[0]),
            unique=0,
            trial_num=trial_num,
            X=X,
            Y=Y,
            Z=Z,
        )
        if normalized == 1:  # Normalized is true
            for file in file_list:  # Goes through each file one at a time
                file_path = os.path.join(
                    input_directory, file
                )  # Creates path to each file

                with open(file_path, "r") as f:  # Opens each file
                    contents = trim_header(file_path)  # Reads each file
                if row_check is None:  # Only proceeds on first iteration
                    row_check = contents.shape[
                        0
                    ]  # Sets row check to size of first file
                    col_check = contents.shape[
                        1
                    ]  # Sets column check to size of first file
                    output = np.full(
                        (101, col_check, len(file_list)), np.nan
                    )  # Initializes output based on the size of the first file
                    output[:, :, file_list.index(file)] = (
                        contents  # Fills first z slice of output with first file
                    )
                else:
                    if (
                        contents.shape[0] != row_check or contents.shape[1] != col_check
                    ):  # Checks if all files are the same size
                        raise ValueError(
                            f"Dimensions of {file} do not match other files.\n\t\t{file} has {contents.shape[0]} rows and {contents.shape[1]} columns.\n\t\tThe test file has {row_check} rows and {col_check} columns."
                        )
                    else:
                        output[:, :, file_list.index(file)] = (
                            contents  # Fills each z slice of output with each file as long as they are correct size
                        )

            data_shape = output.shape
            output_flat = output.reshape(-1, output.shape[-1])
            save_path = os.path.join(output_directory, file_savename)
            if os.path.isfile(save_path):
                response = tk.messagebox.askokcancel(
                    "File Exists",
                    f"The file '{file_savename}' already exists. Do you want to overwrite it?",
                )
                if not response:
                    tk.messagebox.showinfo(
                        "Save Canceled",
                        f"File save of '{file_savename}' canceled.",
                    )
                    return
            with open(save_path, "w") as file:
                file.write(f"({data_shape[0]} {data_shape[1]} {data_shape[2]})\n")
                file.write(f"{var_list}\n")
                file.write(f"({X},{Y},{Z})\n")
                np.savetxt(file, output_flat, fmt="%.8f")
            return

        if normalized == 0:  # Normalized is false
            largest_rows = -1
            common_cols = None
            cols = 0

            for filename in file_list:  # Goes through each file one at a time
                file_path = os.path.join(
                    input_directory, filename
                )  # Creates path to each file
                with open(file_path, "r") as file:  # Opens each file
                    contents = trim_header(file_path)  # Reads each file
                    rows = contents.shape[0]  # Sets row check to size of first file
                    cols = (
                        contents.shape[1] if rows > 0 else 0
                    )  # Sets column check to size of first file
                    if rows > largest_rows:
                        largest_rows = rows  # Iteratively finds largest amount of rows- purpose: preallocate output size
                    if common_cols is None:
                        common_cols = cols
                    elif (
                        cols != common_cols
                    ):  # Checks if all files have the same columns
                        raise ValueError(
                            f"'{filename}' does not have the same number of columns as others."
                        )
            output = np.full(
                (largest_rows, cols, len(file_list)), np.nan
            )  # Initializes output based on the file with largest row count
            for file in file_list:
                file_path = os.path.join(input_directory, file)
                with open(file_path, "r") as f:
                    contents = trim_header(file_path)
                    if contents.shape[0] != output.shape[0]:
                        add_rows = output.shape[0] - contents.shape[0]
                        contents = np.append(
                            contents,
                            np.full((add_rows, contents.shape[1]), np.nan),
                            axis=0,
                        )
                    output[:, :, file_list.index(file)] = contents

            data_shape = output.shape
            output_flat = output.reshape(-1, output.shape[-1])
            save_path = os.path.join(output_directory, file_savename)
            if os.path.isfile(save_path):
                response = tk.messagebox.askokcancel(
                    "File Exists",
                    f"The file '{file_savename}' already exists. Do you want to overwrite it?",
                )
                if not response:
                    tk.messagebox.showinfo(
                        "Save Canceled",
                        f"File save of '{file_savename}' canceled.",
                    )
                    return
            with open(save_path, "w") as file:
                file.write(f"({data_shape[0]} {data_shape[1]} {data_shape[2]})\n")
                file.write(f"{var_list}\n")
                file.write(f"({X},{Y},{Z})\n")
                np.savetxt(file, output_flat, fmt="%.8f")
            return
    except FileNotFoundError as e:
        tk.messagebox.showerror("File Not Found", str(e))
        return
    except ValueError as e:
        tk.messagebox.showerror("Value Error", str(e))
        return
    except TypeError as e:
        tk.messagebox.showerror("Type Error", str(e))
        return
    except NotADirectoryError as e:
        tk.messagebox.showerror("Directory Error", str(e))
        return


def quality_check(batch_input: str, subject_idx: int) -> tuple[plt.Figure, plt.Axes]:
    """This function imports a file from batch() and graphs them to assess curve quality and identify probelmatic data. This is done by plotting however many variables are in the file divided into 3x3 plots.

    INPUTS:
        qual_check_in: Output from batch()
        subject_idx: Subject number indicating position in batch, starting at 1 (z-axis of batch output)

    OUTPUTS:
        plot list of 3x3 subplots, amount depends on number of variables (as in, 18 variables will return two 3x3 plots per subject)

    DEPENDENCIES:
        Matplotlib.pyplot, Numpy, OS

    SEE ALSO:
        batch
        get_vars

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    try:
        file_in = os.path.basename(batch_input)
        true_file, _ = os.path.splitext(file_in)
        qual_check_in, var_list, comp_split, comp_list = batch_reshape(batch_input)
        if qual_check_in.ndim != 3:
            raise ValueError("qual_check_in must be a 3D array.")
        if qual_check_in.shape[1] % len(var_list) != 0:
            raise ValueError(
                f"Data input column size ({qual_check_in.shape[1]}) must be divisible by number of variables ({len(var_list)}) to determine trial amount. Ensure each trial has the same number of variables."
            )
        if qual_check_in.shape[1] % len(var_list) != 0:
            raise ValueError(
                f"Number of variables ({len(var_list)}) must be divisible by number of trials ({qual_check_in.shape[1]})"
            )
        if subject_idx < 0 or subject_idx >= qual_check_in.shape[2]:
            raise ValueError(
                f"Subject_idx ({subject_idx}) must be between 0 and {qual_check_in.shape[2]}."
            )

        components = len(comp_split)  # Determines number of components
        if components < 1 or components > 3:
            raise ValueError(
                f"Components must be a list of length 1-3. Provided list was of length {len(comp_split)}."
            )
        num_3x3_plots = len(var_list) // 9
        if len(var_list) % 9 != 0:  # Checks for floats and rounds up
            num_3x3_plots += 1

        start_col = 0  # Initialize the starting column for the first set of subplots
        plot_list = []  # Initialize an empty list to store the plots

        legend_labels = np.linspace(
            1,
            int((qual_check_in.shape[1] / len(var_list))),
            int((qual_check_in.shape[1] / len(var_list))),
        )  # Generate a list of legend labels based on the number of trials (column size/number of variables)
        legend_labels = [
            f"Trial {int(label)}" for label in legend_labels
        ]  # Append Trial to each label

        for j in range(num_3x3_plots):  # Iterate through the number of 3x3 subplots
            fig, axes = plt.subplots(3, 3, figsize=(10, 8))  # Create subplots
            # fig.tight_layout()
            fig.suptitle(
                f"File Number {subject_idx+1} from '{true_file}' - Page {j+1}"
            )  # Add figure title
            axes = axes.ravel()  # Flatten the axes
            for i, ax in enumerate(axes):  # Iterate through the axes
                plot_comps_idx = (
                    i % components
                )  # Determine which component to add to plot title
                start_idx = start_col + i
                try:
                    ax.set_title(
                        f"{var_list[start_idx]} {comp_list[plot_comps_idx]}"
                    )  # Add title
                    ax.plot(
                        qual_check_in[:, start_idx :: len(var_list), subject_idx]
                    )  # Plot the data for current variable and all trials
                except IndexError:
                    ax.plot([], [])  # set empty plot when end of list is reached
                    break
                plt.subplots_adjust(wspace=0.4, hspace=0.4, top=0.9)  # Adjust spacing

            start_col += 9  # Update the starting column for the next set of subplots
            plot_list.append(fig)  # Append the figure to the plot list
            plt.figlegend(legend_labels, loc="lower center", ncol=5)  # Add the legend

        return plot_list
    except FileNotFoundError as e:
        tk.messagebox.showerror("File Not Found", str(e))
        return
    except ValueError as e:
        tk.messagebox.showerror("Value Error", str(e))
        return
    except TypeError as e:
        tk.messagebox.showerror("Type Error", str(e))
        return
    except NotADirectoryError as e:
        tk.messagebox.showerror("Directory Error", str(e))
        return


def batch_reshape(batch_input: str) -> tuple[npt.NDArray, list, list, list]:
    """This function imports a flattened 3D array from batch() and returns the reshaped data as a 3D numpy array.

    INPUTS:
        batch_input: Output from batch()

    OUTPUTS:
        qual_check_in: 3D array of flattened input data
        var_list: Non-unique list of variable names
        comp_split: List of components (as strings) to graph as in ["X","Z"] or ["X","Y","Z"]
        comp_list: List of components as bools as in [1 1 0] for ["X", "Y"]

    DEPENDENCIES:
        Numpy, OS

    SEE ALSO:
        batch
        get_vars

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    try:
        if batch_input is None:
            raise ValueError("batch_input cannot be None.")
        if batch_input == "":
            raise ValueError("batch_input cannot be an empty string.")
        if not os.path.exists(batch_input):
            raise ValueError(f"{batch_input} does not exist.")
        with open(batch_input, "r") as file:
            shape_values = file.readline().strip("()\n").split()
            var_list = file.readline().strip().replace(",", "").split(" ")
            comp_split = file.readline().strip("()\n").split(",")
            comp_list = []
            if comp_split[0] == "1":
                comp_list.append("X")
            if comp_split[1] == "1":
                comp_list.append("Y")
            if comp_split[2] == "1":
                comp_list.append("Z")
            data_flat = np.loadtxt(file, dtype=float, skiprows=0)
            qual_check_in = data_flat.reshape(
                int(shape_values[0]), int(shape_values[1]), int(shape_values[2])
            )
            return qual_check_in, var_list, comp_split, comp_list
    except ValueError as e:
        tk.messagebox.showerror("Value Error", str(e))
        return


def qual_metadata(batch_input: str) -> int:
    """This function imports a flattened 3D array from batch() and returns the subject count.

    INPUTS:
        batch_input: Output from batch()

    OUTPUTS:
        plot_check: Outputs number

    DEPENDENCIES:
        Numpy, OS

    SEE ALSO:
        batch
        get_vars

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    try:
        if batch_input is None:
            raise ValueError("batch_input cannot be None.")
        if batch_input == "":
            raise ValueError("batch_input cannot be an empty string.")
        if not os.path.exists(batch_input):
            raise ValueError(f"{batch_input} does not exist.")
        with open(batch_input, "r") as file:
            shape_values = file.readline().strip("()\n").split()
            var_list = file.readline().strip().replace(",", "").split(" ")
            sub_count = int(shape_values[2])
            plot_per_sub = len(var_list) % 9
            if not isinstance(plot_per_sub, int):
                raise ValueError(
                    "Plot count not valid. Check input from batch() line 1 to assess shape of array."
                )
            return plot_per_sub, sub_count
    except ValueError as e:
        tk.messagebox.showerror("Value Error", str(e))
        return


def normalize(batched_file_location: str, output_file_location: str) -> None:
    """This function imports a batched output from batch() and normalizes the data to 101 data points, saving with "_Normalized" appended.

    INPUTS:
        batched_file_location: Output from batch()

    OUTPUTS:
        norm_cube: Normalized data

    DEPENDENCIES:
        Numpy

    SEE ALSO:
        batch

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    data_cube, batched_vars, comp_split, comp_list = batch_reshape(
        batched_file_location
    )
    if data_cube.shape[0] == 101:
        result = messagebox.askyesno(
            "Warning",
            "This data appears to have already been normalized to 101 data points. Continue?",
        )
        if not result:
            return

    trials = int(data_cube.shape[1] / len(batched_vars))
    mapped_vars = map(str, batched_vars)
    var_list = ", ".join(mapped_vars)

    def normalize_column(column):
        non_nan_values = column[~np.isnan(column)]
        if len(non_nan_values) == 0:
            return np.full(101, np.nan)
        normalized_values = np.interp(
            np.linspace(0, 1, 101),
            np.linspace(0, 1, len(non_nan_values)),
            non_nan_values,
        )
        return normalized_values

    norm_cube = np.full((101, data_cube.shape[1], data_cube.shape[2]), np.nan)

    for sub_index in range(norm_cube.shape[2]):
        for col_index in range(norm_cube.shape[1]):
            column = data_cube[:, col_index, sub_index]
            float_values = column[np.isfinite(column) & (column.dtype == float)]
            if len(float_values) > 0:
                normalized_values = normalize_column(float_values)
                norm_cube[: len(normalized_values), col_index, sub_index] = (
                    normalized_values
                )
    norm_flat = norm_cube.reshape(-1, norm_cube.shape[-1])
    filename = os.path.basename(batched_file_location).split(".")[0]
    output_original = f"{filename}_Normalized.txt"
    output_path = os.path.join(output_file_location, output_original)
    output_path = output_path.replace(os.path.sep, "/")

    if os.path.isfile(output_path):
        result = messagebox.askyesno(
            "File Exists", "The file already exists. Do you want to overwrite it?"
        )
        if not result:
            return
    else:
        with open(output_path, "w") as file:
            file.write(
                f"({norm_cube.shape[0]} {norm_cube.shape[1]} {norm_cube.shape[2]})\n"
            )
            file.write(f"{var_list}\n")
            file.write(f"({comp_split[0]},{comp_split[1]},{comp_split[2]})\n")
            np.savetxt(file, norm_flat, fmt="%.8f")
            messagebox.showinfo(
                "Normalization Complete", f"File saved to: {output_path}"
            )


def process_cube(norm_cube: str, bool_array: list) -> tuple((npt.NDArray, npt.NDArray)):
    """This function imports a normalized data cube from normalize() and processes the means and standard deviations for ensemble curve generation.

    INPUTS:
        norm_cube: Output from normalize()
        bool_array: Array of booleans denoting which variables to include, the length of which should equal the total variables in the norm_cube

    OUTPUTS:
        processed_means: Array of mean columns corresponding to the order of variables chosen
        processed_std: Array of standard deviation columns corresponding to the order of variables chosen

    DEPENDENCIES:
        Numpy

    SEE ALSO:
        batch

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    trials = int(norm_cube.shape[1] // len(bool_array))
    storage = np.full(
        (norm_cube.shape[0], (sum(bool_array) * trials), norm_cube.shape[2]),
        np.nan,
    )
    intermediate_means = np.full(
        (storage.shape[0], sum(bool_array), storage.shape[2]), np.nan
    )
    intermediate_std = np.full(
        (storage.shape[0], sum(bool_array), storage.shape[2]), np.nan
    )
    bool_array = np.array(bool_array)
    for i in range(trials):
        start_col = i * len(bool_array)
        end_col = (i + 1) * len(bool_array)
        selected_columns = norm_cube[:, start_col:end_col, :][
            :, bool_array.astype(bool), :
        ]
        storage[:, i * sum(bool_array) : (i + 1) * sum(bool_array), :] = (
            selected_columns
        )
    for j in range(storage.shape[2]):
        for i in range(sum(bool_array)):
            intermediate_means[:, i, j] = np.mean(
                storage[:, i :: sum(bool_array), j], axis=1
            )
            intermediate_std[:, i, j] = np.std(
                storage[:, i :: sum(bool_array), j], axis=1
            )

    processed_means = np.mean(intermediate_means, axis=2)
    processed_std = np.mean(intermediate_std, axis=2)
    return processed_means, processed_std


def ensemble_plot(
    mean_array: npt.NDArray,
    std_array: npt.NDArray,
    mean_color: str = "black",
    std_color: str = "lightgrey",
    title: str = None,
    xlabel: str = None,
    ylabel: str = None,
    legend_labels: list = None,
    y_line: bool = 0,
) -> tuple((plt.Figure, plt.Axes)):
    """This function generates ensemble plots from normalized data and returns figure and axes objects as a tuple.

    INPUTS:
        mean_array: First output from process_cube()
        std_array: Second output from process_cube()
        mean_color: Color of the mean line
        std_color: Color of the standard deviation line
        title: Title of the plot
        xlabel: Label of the x-axis
        ylabel: Label of the y-axis
        legend_labels: List of labels for the legend
        y_line: Whether to plot a line at y=0

    OUTPUTS:
        fig: Figure object
        ax: Axes object

    DEPENDENCIES:
        Numpy, Matplotlib.pyplot, SciencePlots (optional)

    SEE ALSO:
        batch

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    try:
        with plt.style.context("science"):
            fig, ax = plt.subplots(figsize=(5, 5))
    except Exception as e:
        print(f"Caught an exception: {e}")
        fig, ax = plt.subplots(figsize=(5, 5))
        params = {
            "font.family": "helvetica",
            "font.size": 10.0,
            "font.weight": "light",
            "axes.labelsize": 10.0,
            "axes.titlesize": 12.0,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 8.0,
        }
        plt.rcParams.update(params)

    x = np.arange(len(mean_array))
    ax.plot(
        x,
        mean_array,
        color=mean_color,
        label=legend_labels[0] if legend_labels else "Mean",
    )

    ax.fill_between(
        x,
        mean_array - std_array,
        mean_array + std_array,
        color=std_color,
        alpha=0.2,
        edgecolor="None",
        label=legend_labels[1] if legend_labels else "Standard Deviation",
    )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.tick_params(axis="both", which="both", right=False, top=False)
    ax.tick_params(axis="x", direction="in")
    ax.tick_params(axis="y", direction="in")

    if y_line == 1:
        y_min, y_max = ax.get_ylim()
        if y_min <= 0 <= y_max:
            ax.axhline(y=0, color="black", linestyle="dashed", linewidth=1)

    legend = ax.legend(loc="best")

    plt.subplots_adjust(
        top=0.85, bottom=0.15, left=0.15, right=0.9, hspace=0.5, wspace=0.5
    )
    legend.get_frame().set_linewidth(0)
    ax.set_xlim(left=0, right=len(mean_array) - 1)
    return fig, ax


def spm_analysis(
    select_a_test: str,
    group_names: list,
    selected_group: str,
    g1_in: str,
    g2_in: str = None,
    g3_in: str = None,
    output_path: str = None,
    alpha: float = 0.05,
    equal_var: bool = False,
    two_tail: bool = True,
    dpi: int = 300,
    g1_color: str = "black",
    g2_color: str = "blue",
    g3_color: str = "red",
    plot_x_label: str = None,
    plot_y_labels: str = None,
) -> None:
    """This function perform a Statistical Parametric Mapping analysis with multiple arguments for customization.

    INPUTS:
        g1_in: Path to the first group data cube
        g2_in: Path to the second group data cube
        output_path: Path to the output directory
        alpha (optional): Significance level
        two_tail (optional): Whether to use the two-tailed or one-tailed test
        equal_var (optional): Whether to assume equal variances
        dpi (optional): Number of dots per inch for individual .TIFF plots
        g1_color (optional): Color of the first group
        g2_color (optional): Color of the second group
        plot_x_label (optional): Label for the x-axis
        group_names (optional): Names of the groups for the legend, as in ["Control", "Experimental"]

    OUTPUTS:
        .TIFF file SPM plots for each variable in the original data cube

    DEPENDENCIES:
        Numpy, spm1d

    SEE ALSO:
        batch

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    test_options = {
        "One-sample t test": spm1d.stats.ttest,
        "Paired t test": spm1d.stats.ttest_paired,
        "Two-sample t test": spm1d.stats.ttest2,
        "One-way ANOVA": spm1d.stats.anova1,
        "One-way Rep. Meas.": spm1d.stats.anova1rm,
    }
    selected_test = test_options[select_a_test]
    group_count = int(selected_group)
    norm_cubes = []
    var_list = []
    comp_list = []
    if plot_y_labels is None or plot_y_labels == [] or plot_y_labels == "":
        result = messagebox.askyesno(
            "Warning",
            "No plot Y-labels provided. Do you want to continue with no labels?",
        )
        if not result:
            return
        else:
            plot_y_labels = None
    else:
        plot_y_labels = pd.read_excel(plot_y_labels, header=None)
    try:
        # if any(path is None or path == "" for path in (g1_in, g2_in, g3_in)):
        #     raise ValueError("One or more input file paths are not specified.")
        # if output_path is None or output_path == "":
        #     raise ValueError("Output directory path is not specified.")
        # if not any(os.path.exists(path) for path in (g1_in, g2_in, g3_in)):
        #     raise FileNotFoundError("One or more input files do not exist.")
        if not os.path.exists(output_path):
            raise FileNotFoundError("Output directory does not exist.")
        if 0 > float(alpha) < 1:
            raise ValueError("Significance level must be between 0 and 1.")
        try:
            int(dpi)
        except TypeError:
            raise TypeError("DPI must be an integer.")
        if 299 > int(dpi) < 801:
            raise ValueError("DPI value must be greater than 300 and less than 800.")

        for group in range(1, group_count + 1):
            group_exists = f"g{group}_in"
            if group_exists in locals() and locals()[group_exists] is not None:
                group_norm_cube, group_var_list, _, group_comp_list = batch_reshape(
                    locals()[f"g{group}_in"]
                )
                stripped_lists = [
                    (var.replace("Right", "").replace("Left", ""))
                    for var in group_var_list
                ]

                if len(group_var_list) % len(group_comp_list) != 0:
                    raise ValueError(
                        "Number of variables not divisible by the number of components."
                    )
                try:
                    if len(group_var_list) != len(plot_y_labels):
                        raise ValueError(
                            "Number of variables not equal to number of plot Y-labels."
                        )
                except:
                    pass

                norm_cubes.append(group_norm_cube)
                var_list = stripped_lists
                comp_list = group_comp_list

        cube_shape_check = norm_cubes[0].shape
        if any(cube.shape != cube_shape_check for cube in norm_cubes):
            raise ValueError(
                "Inconsistent norm_cubes shapes across iterations. Check all group(s) input data shape."
            )
        if any(cube.shape[0] != 101 for cube in norm_cubes):
            raise ValueError(
                "Data for the SPM functions must be normalized to 101 points. Check all group(s) input data shape."
            )

        raw_var_list = [
            f"{original} {xyz}"
            for original, xyz in zip(
                var_list, comp_list * (len(var_list) // len(comp_list) + 1)
            )
        ]
        true_var_list = [
            "".join(
                [
                    (
                        " " + char
                        if char.isupper()
                        and i > 0
                        and raw_var_list[idx][i - 1].islower()
                        else char
                    )
                    for i, char in enumerate(word)
                ]
            )
            for idx, word in enumerate(raw_var_list)
        ]

        output_dir = output_path
        pdf_out = os.path.join(output_dir, "All_SPM_Plots.pdf")
        with PdfPages(pdf_out) as pdf:
            tiff_path = os.path.join(output_dir, f"{true_var_list[0]}.tiff")
            if os.path.isfile(tiff_path):
                response = messagebox.askyesno(
                    "File Already Exists",
                    f"It looks like the .TIFF files already exist. Do you want to overwrite them?",
                )
                if not response:
                    return
            for i in range(0, len(true_var_list)):
                if selected_test == spm1d.stats.ttest_paired:
                    t = selected_test(
                        *([norm_cube[:, i, :].T for norm_cube in norm_cubes]),
                    )  # no equal variance for this test
                elif selected_test == spm1d.stats.anova1:
                    t = spm1d.stats.anova1(
                        tuple(norm_cube[:, i, :].T for norm_cube in norm_cubes),
                        equal_var=equal_var,
                    )  # test requires groups to be in a tuple
                else:
                    t = selected_test(
                        *([norm_cube[:, i, :].T for norm_cube in norm_cubes]),
                        equal_var=equal_var,
                    )  # all other (current) tests
                if selected_test == spm1d.stats.anova1:
                    ti = t.inference(
                        alpha=float(alpha)
                    )  # no two_tailed for one way ANOVA
                else:
                    ti = t.inference(alpha=float(alpha), two_tailed=two_tail)

                fig, axes = plt.subplots(1, 2, figsize=(10, 4))
                plt.subplots_adjust(left=0.1, right=0.95, bottom=0.2, hspace=0.4)

                ax = axes[0]
                for group_num, norm_cube in enumerate(norm_cubes, start=1):
                    data = norm_cube[:, i, :].T
                    line_color = locals()[f"g{group_num}_color"]
                    spm1d.plot.plot_mean_sd(
                        data,
                        linecolor=line_color,
                        facecolor=line_color,
                        ax=ax,
                        label=group_names[group_num - 1],
                    )
                ax.axhline(y=0, color="k", linestyle=":")
                ax.set_xlabel(plot_x_label)
                try:
                    ax.set_ylabel(plot_y_labels.iloc[i, 0])
                except AttributeError:
                    pass
                ax.set_title(f"{true_var_list[i]}")

                ax = axes[1]
                ti.plot(ax=ax)
                ti.plot_threshold_label(fontsize=10, ax=ax)
                ti.plot_p_values(size=12, offset_all_clusters=(0, 0.3), ax=ax)
                ax.set_xlabel(plot_x_label)

                fig.legend(
                    loc="lower center",
                    bbox_to_anchor=(0.3, 0),
                    fontsize=10,
                    ncols=int(selected_group),
                )

                tiff_path = os.path.join(output_dir, f"{true_var_list[i]}.tiff")
                plt.savefig(tiff_path, dpi=int(dpi))
                pdf.savefig()

                plt.close()
        tk.messagebox.showinfo(
            "Save Complete",
            f"SPM conducted with the following parameters:\n\nGroup(s): {selected_group}\nTest: {selected_test.__name__}\nEqual Variance: {equal_var}\nAlpha: {alpha}\nTwo Tailed: {two_tail}\n\nAll plots have been saved here: {output_dir}",
        )
    except ValueError as e:
        tk.messagebox.showerror("Value Error", str(e))
        return
    except TypeError as e:
        tk.messagebox.showerror("Type Error", str(e))
        return
    except FileNotFoundError as e:
        tk.messagebox.showerror("File Not Found Error", str(e))
        return
