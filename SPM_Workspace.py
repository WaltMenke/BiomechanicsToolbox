import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ttkbootstrap as ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import re
import numpy.typing as npt
import spm1d
import ToolboxFunctions as bf


def spm(
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
    group_names: list = ["Control", "Experimental"],
) -> None:
    """This function perform a 2-group Statistical Parametric Mapping analysis with multiple arguments for customization.

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
        Numpy

    SEE ALSO:
        v3d_batch

    Created by Walt Menke (2023) - wmenke597@gmail.com
    """
    test_options = {
        "One-sample t test": spm1d.stats.ttest,
        "Paired t test": spm1d.stats.ttest_paired,
        "Two-sample t test": spm1d.stats.ttest2,
        "One-way ANOVA": spm1d.stats.anova1,
        "One-way Rep. Meas.": spm1d.stats.anova1rm,
    }
    # selected_test=test_dropdown.get()
    selected_group = "1"
    select_a_test = "One-way ANOVA"
    selected_test = test_options[select_a_test]
    group_names = ["Control", "Group 1", "Group 2"]

    norm_cubes = []

    # Iterate over possible groups (1, 2, 3)
    try:
        for group_num in range(1, 4):
            var_name = f"norm_cube_{group_num}"
            if hasattr(globals(), var_name):
                norm_cube, var_list, _, comp_list = bf.v3d_batched_reshape(
                    globals()[f"g{group_num}_in"]
                )

                stripped_lists = [
                    (var.replace("Right", "").replace("Left", "")) for var in var_list
                ]

                true_var_list, _ = zip(*stripped_lists)
                var_list = true_var_list

                if len(var_list) % len(comp_list) != 0:
                    raise ValueError(
                        "Number of variables not divisible by the number of components."
                    )

                norm_cubes.append(locals()[var_name])

        raw_var_list = [
            f"{original} {xyz}"
            for original, xyz in zip(
                var_list, comp_list * (len(var_list) // len(comp_list) + 1)
            )
        ]
        true_var_list = [
            "".join(
                [
                    " " + char
                    if char.isupper() and i > 0 and raw_var_list[idx][i - 1].islower()
                    else char
                    for i, char in enumerate(word)
                ]
            )
            for idx, word in enumerate(raw_var_list)
        ]

        group_names = [name.strip() for name in group_names.split(",")]

        output_dir = output_path
        pdf_out = os.path.join(output_dir, "All_SPM_Plots.pdf")

        with PdfPages(pdf_out) as pdf:
            tiff_path = os.path.join(output_dir, f"{true_var_list[0]}.tiff")
            if os.path.exists(tiff_path):
                response = messagebox.askyesno(
                    "File Already Exists",
                    f"It looks like the .TIFF files already exist. Do you want to overwrite them?",
                )
                if not response:
                    return
            for i in range(0, len(true_var_list)):
                if selected_group == "1":
                    t = selected_test(norm_cubes[0][:, i, :].T, equal_var=equal_var)
                elif selected_group == "2":
                    t = selected_test(
                        *([norm_cube[:, i, :].T for norm_cube in norm_cubes]),
                        equal_var=equal_var,
                    )
                elif selected_group == "3":
                    t = selected_test(
                        *([norm_cube[:, i, :].T for norm_cube in norm_cubes]),
                        equal_var=equal_var,
                    )
            ti = t.inference(alpha=float(alpha), two_tailed=two_tail)

            # fig, axes = plt.subplots(1, 2, figsize=(10, 4))
            # plt.subplots_adjust(left=0.1, right=0.95, bottom=0.2, hspace=0.4)

            # ax = axes[0]
            # num_groups = int(selected_group)

            # for group_num in range(1, num_groups + 1):
            #     data = globals()[f"norm_cube_{group_num}"][:, i, :].T
            #     line_color = globals()[f"g{group_num}_color"]
            #     spm1d.plot.plot_mean_sd(
            #         data,
            #         linecolor=line_color,
            #         facecolor=line_color,
            #         ax=ax,
            #         label=group_names[group_num - 1],
            #     )
            # ax.axhline(y=0, color="k", linestyle=":")
            # ax.set_xlabel(plot_x_label)
            # ax.set_title(f"{true_var_list[i]}")

            # ax = axes[1]
            # ti.plot(ax=ax)
            # ti.plot_threshold_label(fontsize=10, ax=ax)
            # ti.plot_p_values(size=12, offset_all_clusters=(0, 0.3), ax=ax)
            # ax.set_xlabel(plot_x_label)

            # fig.legend(
            #     loc="lower center",
            #     bbox_to_anchor=(0.3, 0),
            #     fontsize=10,
            #     ncols=2,
            # )

            # tiff_path = os.path.join(output_dir, f"{true_var_list[i]}.tiff")
            # plt.savefig(tiff_path, dpi=dpi)
            # pdf.savefig()

            # plt.close()
        tk.messagebox.showinfo(
            "Save Complete", f"All SPM plots have been saved here: {output_dir}"
        )
    except ValueError as e:
        tk.messagebox.showerror("Value Error", str(e))
        return


# select_a_test = input(
#     "Select a statistical test:\nOne-sample t test\nPaired t test\nTwo-sample t test\nOne-way ANOVA\nOne-way Rep. Meas.\n"
# )
# selected_test=test_options.get(select_a_test)

# t = spm1d.stats.ttest2(
#     norm_cube_1[:, i, :].T, norm_cube_2[:, i, :].T, equal_var=equal_var
# )
# ti = t.inference(alpha=float(alpha), two_tailed=two_tail)
# # get_test=getattr(spm1d.)
