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
                            messagebox.showwarning(
                                "Warning",
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
        messagebox.showwarning(
            "Warning",
            "Group selected was larger than specified in the parameters! Re-select group and try again.",
        )
        return
    messagebox.showinfo("Load Successful", "SPM tab parameters loaded!")
