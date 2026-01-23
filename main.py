import os
import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import pandas as pd
from pipeline import Pipeline

class ExtractionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Groq Data Extraction Pipeline")
        self.root.geometry("800x600")
        
        self.pipeline = Pipeline()
        self.current_data = None
        self.selected_file = None

        # --- UI Layout ---
        
        # Header
        header = tk.Label(root, text="Public Data Extraction & Structuring", font=("Arial", 16, "bold"), pady=10)
        header.pack()

        # Input Frame
        frame_input = tk.Frame(root, pady=10)
        frame_input.pack()
        
        self.btn_select = tk.Button(frame_input, text="Select PDF File", command=self.select_file, width=20, height=2)
        self.btn_select.grid(row=0, column=0, padx=5)
        
        self.lbl_file = tk.Label(frame_input, text="No file selected", fg="gray")
        self.lbl_file.grid(row=0, column=1, padx=5)
        
        # Action Frame
        frame_action = tk.Frame(root, pady=10)
        frame_action.pack()
        
        self.btn_run = tk.Button(frame_action, text="Run Pipeline", command=self.run_pipeline, state=tk.DISABLED, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_run.pack(side=tk.LEFT, padx=10)
        
        self.btn_download = tk.Button(frame_action, text="Download CSV", command=self.download_csv, state=tk.DISABLED, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_download.pack(side=tk.LEFT, padx=10)

        # Output Display
        self.txt_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=25)
        self.txt_output.pack(padx=20, pady=10, expand=True, fill="both")
        
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.selected_file = file_path
            self.lbl_file.config(text=os.path.basename(file_path), fg="black")
            self.btn_run.config(state=tk.NORMAL)
            self.txt_output.delete(1.0, tk.END)
            self.current_data = None
            self.btn_download.config(state=tk.DISABLED)

    def run_pipeline(self):
        if not self.selected_file:
            return
            
        self.txt_output.delete(1.0, tk.END)
        self.txt_output.insert(tk.END, f"Processing {os.path.basename(self.selected_file)}...\nThis may take a moment...\n")
        self.root.update()
        
        try:
            # Run the pipeline
            self.current_data = self.pipeline.run(self.selected_file, save_json=False)
            
            # Display Result
            self.txt_output.delete(1.0, tk.END)
            self.txt_output.insert(tk.END, json.dumps(self.current_data, indent=4))
            
            self.btn_download.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "Extraction complete!")
            
        except Exception as e:
            self.txt_output.insert(tk.END, f"\nError: {e}")
            messagebox.showerror("Error", f"Pipeline failed: {e}")

    def download_csv(self):
        if not self.current_data:
            return
            
        # Strategy: We can save tables or key entities. 
        # For this example, let's flatten tables and entities into separate sheets or just one main CSV.
        # User requested "structured csv", so let's ask where to save.
        
        # Calculate next available output name
        output_name = "output 1"
        i = 1
        while os.path.exists(f"{output_name}.csv") or os.path.exists(f"{output_name}.xlsx"):
            i += 1
            output_name = f"output {i}"
            
        save_path = filedialog.asksaveasfilename(
            initialfile=output_name,
            defaultextension=".csv", 
            filetypes=[("CSV File", "*.csv"), ("Excel File", "*.xlsx")]
        )
        if not save_path:
            return

        try:
            # Flatten data for CSV
            # 1. Entities
            entities = self.current_data.get("key_entities", [])
            df_entities = pd.DataFrame(entities, columns=["Entity"])
            
            # 2. Summary
            summary = self.current_data.get("summary", "")
            df_summary = pd.DataFrame([summary], columns=["Summary"])
            
            # 3. Tables (Flattening the first table found or mixing)
            tables = self.current_data.get("tables", [])
            dfs = {}
            dfs["Summary"] = df_summary
            dfs["Entities"] = df_entities
            
            for i, tbl in enumerate(tables):
                title = tbl.get("title", f"Table_{i+1}")
                data = tbl.get("data", [])
                if isinstance(data, list) and len(data) > 0:
                    dfs[title] = pd.DataFrame(data)
                elif isinstance(data, str):
                     # If model returned string for data, just put it in a cell
                     dfs[title] = pd.DataFrame([data], columns=["Data"])

            # If saving as CSV, we might need a workaround for multiple tables (e.g., separate files or just main table)
            if save_path.endswith(".csv"):
                # Append all to one CSV with spacers
                with open(save_path, 'w', newline='', encoding='utf-8') as f:
                    for name, df in dfs.items():
                        f.write(f"--- {name} ---\n")
                        df.to_csv(f, index=False)
                        f.write("\n")
            else:
                # Excel is better for multiple sheets
                with pd.ExcelWriter(save_path) as writer:
                    for name, df in dfs.items():
                        # Sheet name limit
                        sheet_name = name[:30]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
            messagebox.showinfo("Saved", f"Data saved to {save_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExtractionApp(root)
    root.mainloop()
