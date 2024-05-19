import tkinter as tk
from tkinter import ttk
import ast
from pathlib import Path  # Import Path from pathlib
import threading



class SettingsApp:
    def __init__(self, master):
        self.master = master

        self.master.title("Data Settings")
        self.master.geometry("800x600")  # Set the initial size of the window

        self.tabControl = ttk.Notebook(self.master)

        # Create a tab for Task data
        self.tab_task = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_task, text="Task")

        # Create a tab for Staff data
        self.tab_staff = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_staff, text="Staff")

        self.tab_assignor = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_assignor, text="Assignor")

        self.tabControl.pack(expand=1, fill="both", padx=10, pady=10)

        # Create task_listbox and staff_listbox
        self.task_listbox = tk.Listbox(self.tab_task, selectmode=tk.SINGLE)
        self.task_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.staff_listbox = tk.Listbox(self.tab_staff, selectmode=tk.SINGLE)
        self.staff_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.assignor_listbox = tk.Listbox(self.tab_assignor, selectmode=tk.SINGLE)
        self.assignor_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Load data from Task.py and Staff.py
        self.task_data = {}
        self.staff_data = {}
        self.assignor_data = {}

        self.load_data_in_thread(self.load_task_data)
        self.load_data_in_thread(self.load_staff_data)
        self.load_data_in_thread(self.load_assignor_data)

        # Populate Listbox widgets with data
        self.populate_listbox(self.task_listbox, self.task_data)
        self.populate_listbox(self.staff_listbox, self.staff_data)
        self.populate_listbox(self.assignor_listbox, self.assignor_data)


        # Create buttons for operations
        self.create_buttons()

        # Check selection every second
        self.start_check_selection_thread()

        self.inner_frame = None  # Initialize inner_frame as an instance attribute


    def load_data_in_thread(self, load_function):
        threading.Thread(target=load_function).start()
    def check_selection(self):
        # Check if the task_listbox widget exists before accessing it
        if hasattr(self, 'task_listbox') and self.task_listbox.winfo_exists():
            task_selection = self.task_listbox.curselection()
            if task_selection:
                print("Task Listbox Selection:", self.task_listbox.get(task_selection))

        # Check if the staff_listbox widget exists before accessing it
        if hasattr(self, 'staff_listbox') and self.staff_listbox.winfo_exists():
            staff_selection = self.staff_listbox.curselection()
            if staff_selection:
                print("Staff Listbox Selection:", self.staff_listbox.get(staff_selection))

        # Check if the assignor_listbox widget exists before accessing it
        if hasattr(self, 'assignor_listbox') and self.assignor_listbox.winfo_exists():
            assignor_selection = self.assignor_listbox.curselection()
            if assignor_selection:
                print("Assignor Listbox Selection:", self.assignor_listbox.get(assignor_selection))

        # Schedule the next check after 500 ms (0.5 second)
        self.master.after(500, self.check_selection)

    def start_check_selection_thread(self):
        thread = threading.Thread(target=self.check_selection)
        thread.daemon = True  # Daemonize thread to exit when the main program exits
        thread.start()
    def load_settings_data(self):
        # Load data from Setting.py file
        file_path = "data/Setting.py"
        try:
            with open(file_path, "r") as file:
                data_lines = file.readlines()
                settings_data = {}
                for line in data_lines:
                    # Skip lines starting with '#' (comments) or empty lines
                    if not line.strip() or line.strip().startswith('#'):
                        continue
                    # Split each line at '=' to get the key and value pair
                    key, value = line.split('=')
                    key = key.strip()  # Remove any leading/trailing whitespace
                    value = value.strip()  # Remove leading/trailing whitespace
                    settings_data[key] = value
                return settings_data
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return {}
        except Exception as e:
            print(f"Error loading settings data: {e}")
            return {}

    def open_setting_window(self):
        setting_window = tk.Toplevel(self.master)
        setting_window.title("Setting")
        setting_window.geometry("600x1000+500+0")  # Example geometry

        # Create a frame to hold the content and scrollbar
        frame = ttk.Frame(setting_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas widget
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=scrollbar.set)

        # Create another frame inside the canvas to hold the settings content
        self.inner_frame = ttk.Frame(canvas)  # Update inner_frame as an instance attribute
        canvas.create_window((0, 0), window=self.inner_frame, anchor=tk.NW)

        icon_path = Path(__file__).resolve().parent / 'data' / 'icon.ico'
        setting_window.iconbitmap(icon_path)
        # Load settings data
        settings_data = self.load_settings_data()

        # Create labels and entry widgets for settings data
        row = 0
        for key, value in settings_data.items():
            label = ttk.Label(self.inner_frame, text=f"{key}:")
            label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            entry = ttk.Entry(self.inner_frame, width=60)
            entry.insert(0, value)  # Insert the current value
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            row += 1

        # Update the scroll region of the canvas
        self.inner_frame.update_idletasks()  # Update the inner frame to calculate its size
        canvas.config(scrollregion=canvas.bbox("all"))

        canvas.bind_all("<MouseWheel>", lambda event: self.on_mousewheel(event, canvas))

        # Save button
        save_button = ttk.Button(setting_window, text="Save", command=lambda: self.save_settings(setting_window))
        save_button.pack(pady=10)

    def on_mousewheel(self, event, canvas):
        # Perform vertical scrolling based on mousewheel movement
        if event.delta < 0:
            canvas.yview_scroll(1, "units")
        else:
            canvas.yview_scroll(-1, "units")

    def save_settings(self, setting_window):
        settings_data = {}
        old_settings_data = self.load_settings_data().copy()

        # Update settings_data from user input - Replace with your UI logic
        for child in self.inner_frame.winfo_children():  # Use self.inner_frame here
            if isinstance(child, ttk.Entry):
                setting_key = child.winfo_name().split("_entry")[0]  # Extract setting key
                settings_data[setting_key] = child.get()

        # Save settings
        try:
            result_dict = {f'NewKey{i}': value for i, value in enumerate(settings_data.values(), 1)}
            # Map values to old_settings_data keys
            new_result_dict = {key: result_dict.get(f'NewKey{i}', 0) for i, key in
                               enumerate(old_settings_data.keys(), 1)}

            with open("data/Setting.py", "w") as file:
                file.write("# Settings\n\n")
                for key, value in new_result_dict.items():
                    file.write(f"{key} = {value}\n")  # Wrap value in quotes
            print("Settings saved.")
            setting_window.destroy()
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_assignor_data(self):
        file_path = "data/Assignor.py"  # Adjust file path as needed
        try:
            with open(file_path, "r") as file:
                data_str = file.read()
                module = ast.parse(data_str)
                for node in module.body:
                    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                        name = node.targets[0].id
                        if name == "conversion_dict_Assignor":
                            self.assignor_data = ast.literal_eval(ast.unparse(node.value))
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except SyntaxError as e:
            print(f"SyntaxError in {file_path}: {e}")

    def load_task_data(self):
        file_path = "data/Task.py"  # Adjust file path as needed
        try:
            with open(file_path, "r") as file:
                data_str = file.read()
                module = ast.parse(data_str)
                for node in module.body:
                    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                        name = node.targets[0].id
                        if name == "conversion_dict_Task":
                            self.task_data = ast.literal_eval(ast.unparse(node.value))
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except SyntaxError as e:
            print(f"SyntaxError in {file_path}: {e}")

    def load_staff_data(self):
        file_path = "data/Staff.py"  # Adjust file path as needed
        try:
            with open(file_path, "r") as file:
                data_str = file.read()
                module = ast.parse(data_str)
                for node in module.body:
                    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                        name = node.targets[0].id
                        if name == "conversion_dict_Staff":
                            self.staff_data = ast.literal_eval(ast.unparse(node.value))
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except SyntaxError as e:
            print(f"SyntaxError in {file_path}: {e}")
    def populate_listbox(self, listbox, data):
        # Populate a Listbox widget with data
        listbox.delete(0, tk.END)
        for key, value in data.items():
            item_text = f"{key}: {', '.join(value) if isinstance(value, list) else value}"
            listbox.insert(tk.END, item_text)


    def save_task_data(self):
        file_path = "data/Task.py"  # Adjust file path as needed
        try:
            with open(file_path, "w") as file:
                file.write("conversion_dict_Task = {\n")
                for key, value in self.task_data.items():
                    if isinstance(value, list):
                        value_str = ', '.join(value)
                        file.write(f"    '{key}': [{value_str}],\n")  # Wrap list values in square brackets
                    else:
                        file.write(f"    '{key}': '{value}',\n")  # Wrap string values in single quotes
                file.write("}\n")
            print("Task data saved.")
            # Do not refresh UI here; handle it separately after saving in the main application logic
        except Exception as e:
            print(f"Error saving task data: {e}")
    def save_assignor_data(self):
        file_path = "data/Assignor.py"  # Adjust file path as needed
        try:
            with open(file_path, "w") as file:
                file.write("conversion_dict_Assignor = {\n")
                for key, value in self.assignor_data.items():
                    if isinstance(value, list):
                        value_str = ', '.join(f"'{item}'" for item in value)
                        file.write(f"    '{key}': [{value_str}],\n")
                    else:
                        file.write(f"    '{key}': '{value}',\n")
                file.write("}\n")
            print("Assignor data saved.")
        except Exception as e:
            print(f"Error saving assignor data: {e}")

    def save_staff_data(self):
        file_path = "data/Staff.py"  # Adjust file path as needed
        try:
            with open(file_path, "w") as file:
                file.write("conversion_dict_Staff = {\n")
                for key, value in self.staff_data.items():
                    key_str = repr(key)  # Use repr to handle both int and str keys correctly
                    if isinstance(value, list):
                        value_str = ', '.join(map(repr, value))  # Use repr for each item in the list
                        file.write(f"    {key_str}: [{value_str}],\n")  # Wrap list values in square brackets
                    else:
                        value_str = repr(value)  # Use repr for string values
                        file.write(f"    {key_str}: {value_str},\n")  # No quotes for string values
                file.write("}\n")
            print("Staff data saved.")
            # Do not refresh UI here; handle it separately after saving in the main application logic
        except Exception as e:
            print(f"Error saving staff data: {e}")

    def create_input_boxes(self, parent, data, is_staff=False, is_task=False):
        self.keys_values_listbox = tk.Listbox(parent, selectmode=tk.SINGLE)
        self.keys_values_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        if is_staff and is_task:
            for key, values in data.items():
                item_text = f"{key}: {', '.join(values)}"
                self.keys_values_listbox.insert(tk.END, item_text)
        else:
            for key, value in data.items():
                item_text = f"{key}: {value}"
                self.keys_values_listbox.insert(tk.END, item_text)

    def create_buttons(self):
        # Frame to hold the buttons in the same row
        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=10)


        # Configure button style
        style = ttk.Style()
        style.configure('ModernGradient.TButton',
                        background='blue',
                        foreground='black',
                        borderwidth=0,
                        font=('Arial', 11, 'bold'))

        style.map('ModernGradient.TButton',
                  background=[('active', '#d0d0d0'), ('pressed', '#c0c0c0')],
                  foreground=[('pressed', 'white'), ('active', 'black')])


        add_button = ttk.Button(button_frame, text="Add", command=self.open_add_window, style='ModernGradient.TButton')
        add_button.pack(side=tk.LEFT, padx=5)

        # Delete button
        delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_key,style='ModernGradient.TButton')
        delete_button.pack(side=tk.LEFT, padx=5)

        # Edit button (for demonstration)
        edit_button = ttk.Button(button_frame, text="Edit", command=self.edit_key_value,style='ModernGradient.TButton')
        edit_button.pack(side=tk.LEFT, padx=5)

        # Setting button (previously Save button)
        setting_button = ttk.Button(button_frame, text="Setting", command=self.open_setting_window,
                                    style='ModernGradient.TButton')
        setting_button.pack(side=tk.LEFT, padx=5)
    def delete_key(self):
        task_selection = self.task_listbox.curselection()
        if task_selection:  # Check if there is a selection in the task listbox
            selected_index = task_selection[0]  # Get the first selected index
            item_text = self.task_listbox.get(selected_index)  # Get the text of the selected item
            key_to_delete, _ = item_text.split(": ")  # Extract the key to delete
            if key_to_delete in self.task_data:
                del self.task_data[key_to_delete]
                self.save_task_data()  # Save task data after deleting key
                print(f"Key '{key_to_delete}' deleted from Task data.")
                self.refresh_task_listbox()  # Refresh Task listbox after deleting key
            else:
                print(f"Key '{key_to_delete}' not found in Task data.")
        else:
            print("No key selected in Task listbox.")

        staff_selection = self.staff_listbox.curselection()
        if staff_selection:  # Check if there is a selection in the staff listbox
            selected_index = staff_selection[0]  # Get the first selected index
            item_text = self.staff_listbox.get(selected_index)  # Get the text of the selected item
            key_to_delete, _ = item_text.split(": ")  # Extract the key to delete
            key_to_delete = int(key_to_delete)
            if key_to_delete in self.staff_data:
                del self.staff_data[key_to_delete]
                self.save_staff_data()  # Save staff data after deleting key
                print(f"Key '{key_to_delete}' deleted from Staff data.")
                self.refresh_staff_listbox()  # Refresh Staff listbox after deleting key
            else:
                print(f"Key '{key_to_delete}' not found in Staff data.")
        else:
            print("No key selected in Staff listbox.")

        assignor_selection = self.assignor_listbox.curselection()
        if assignor_selection:  # Check if there is a selection in the assignor listbox
            selected_index = assignor_selection[0]  # Get the first selected index
            item_text = self.assignor_listbox.get(selected_index)  # Get the text of the selected item
            key_to_delete, _ = item_text.split(": ")  # Extract the key to delete
            if key_to_delete in self.assignor_data:
                del self.assignor_data[key_to_delete]
                self.save_assignor_data()  # Save assignor data after deleting key
                print(f"Key '{key_to_delete}' deleted from Assignor data.")
                self.refresh_assignor_listbox()  # Refresh Assignor listbox after deleting key
            else:
                print(f"Key '{key_to_delete}' not found in Assignor data.")
        else:
            print("No key selected in Assignor listbox.")

    def open_add_window(self):
        current_tab = self.tabControl.index(self.tabControl.select())
        if current_tab == 0:  # Task tab index is 0
            self.add_window = tk.Toplevel(self.master)
            self.add_window.title("Add Key and XPath")

            key_label = ttk.Label(self.add_window, text="Key:")
            key_label.pack(pady=5)
            self.key_entry = ttk.Entry(self.add_window, width=30)
            self.key_entry.pack(pady=5)

            value_label = ttk.Label(self.add_window, text="XPath:")
            value_label.pack(pady=5)
            self.value_entry = ttk.Entry(self.add_window, width=30)
            self.value_entry.pack(pady=5)

            save_button = ttk.Button(self.add_window, text="Save", command=self.save_new_key_value)
            save_button.pack(pady=10)
        elif current_tab == 1:  # Staff tab index is 1
            self.add_window = tk.Toplevel(self.master)
            self.add_window.title("Add Key and XPath")

            key_label = ttk.Label(self.add_window, text="Key:")
            key_label.pack(pady=5)
            self.key_entry = ttk.Entry(self.add_window, width=30)
            self.key_entry.pack(pady=5)

            value_label = ttk.Label(self.add_window, text="XPath:")
            value_label.pack(pady=5)
            self.value_entry = ttk.Entry(self.add_window, width=30)
            self.value_entry.pack(pady=5)

            save_button = ttk.Button(self.add_window, text="Save", command=self.save_new_key_value)
            save_button.pack(pady=10)
        elif current_tab == 2:  # Assignor tab index is 2
            self.add_window = tk.Toplevel(self.master)
            self.add_window.title("Add Key and XPath")

            key_label = ttk.Label(self.add_window, text="Key:")
            key_label.pack(pady=5)
            self.key_entry = ttk.Entry(self.add_window, width=30)
            self.key_entry.pack(pady=5)

            value_label = ttk.Label(self.add_window, text="Value:")
            value_label.pack(pady=5)
            self.value_entry = ttk.Entry(self.add_window, width=30)
            self.value_entry.pack(pady=5)

            save_button = ttk.Button(self.add_window, text="Save", command=self.save_new_assignor_key_value)
            save_button.pack(pady=10)
        else:
            print("Invalid tab selection.")  # This should not occur under normal circumstances

    def save_new_assignor_key_value(self):
        new_key = self.key_entry.get()
        new_value = self.value_entry.get()
        if new_key and new_value:
            if new_key in self.assignor_data:
                print(f"Key '{new_key}' already exists in Assignor data.")
            else:
                self.assignor_data[new_key] = new_value
                print(f"Key '{new_key}' added with value '{new_value}' to Assignor data.")
                self.save_assignor_data()
                self.refresh_assignor_listbox()
                self.refresh_input_boxes()
                self.add_window.destroy()  # Close the add window
        else:
            print("Please provide both key and value.")

    def save_new_key_value(self):
        new_key = self.key_entry.get()
        new_value = self.value_entry.get()
        if new_key and new_value:
            # Check if the currently selected tab is the Task tab
            if self.tabControl.tab(self.tabControl.select(), "text") == "Task":
                self.task_data[new_key] = new_value
                self.save_task_data()  # Save task data after adding new key-value pair
                print(f"Key '{new_key}' added with value '{new_value}' to Task data.")
                self.refresh_task_listbox()  # Refresh Task listbox after adding new key-value pair
            elif self.tabControl.tab(self.tabControl.select(), "text") == "Staff":
                try:
                    # Convert the key to an integer without quotes
                    new_key_int = int(new_key)
                    # Convert the value string to a list of strings
                    values_list = new_value.split(',')
                    self.staff_data[new_key_int] = values_list
                    self.save_staff_data()  # Save staff data after adding new key-value pair
                    print(f"Key '{new_key_int}' added with value '{values_list}' to Staff data.")
                    self.refresh_staff_listbox()  # Refresh Staff listbox after adding new key-value pair
                except ValueError:
                    print("Error: Please enter a valid integer key.")
            elif self.tabControl.tab(self.tabControl.select(), "text") == "Assignor":
                try:
                    # Convert the key to an integer without quotes
                    new_key_int = int(new_key)
                    # Convert the value string to a list of strings
                    values_list = new_value.split(',')
                    self.assignor_data[new_key_int] = values_list
                    self.save_assignor_data()  # Save assignor data after adding new key-value pair
                    print(f"Key '{new_key_int}' added with value '{values_list}' to Assignor data.")
                    self.refresh_assignor_listbox()  # Refresh Assignor listbox after adding new key-value pair
                except ValueError:
                    print("Error: Please enter a valid integer key.")
            self.add_window.destroy()  # Close the add window
        else:
            print("Please provide both key and value.")

    def edit_key_value(self):
        selected_indices_task = self.task_listbox.curselection()
        selected_indices_staff = self.staff_listbox.curselection()
        selected_indices_assignor = self.assignor_listbox.curselection()

        if selected_indices_task:  # Check if there is a selection in the task listbox
            selected_index_task = selected_indices_task[0]  # Get the first selected index for Task data
            item_text_task = self.task_listbox.get(selected_index_task)  # Get the text of the selected item

            key_to_edit_task, _ = item_text_task.split(": ")  # Extract the key to edit for Task data

            # Open the edit window with existing key and value for editing for Task data
            self.open_edit_window(key=key_to_edit_task, value=self.task_data[key_to_edit_task])
        elif selected_indices_staff:  # Check if there is a selection in the staff listbox
            selected_index_staff = selected_indices_staff[0]  # Get the first selected index for Staff data
            item_text_staff = self.staff_listbox.get(selected_index_staff)  # Get the text of the selected item
            key_to_edit_staff, _ = item_text_staff.split(": ")  # Extract the key to edit for Staff data

            # Check if key exists in staff data
            if int(key_to_edit_staff) in self.staff_data:
                # Open the edit window with existing key and value for editing for Staff data
                self.open_edit_window(key=key_to_edit_staff, value=self.staff_data[int(key_to_edit_staff)])
            else:
                print(f"Key '{key_to_edit_staff}' not found in Staff data.")

        elif selected_indices_assignor:  # Check if there is a selection in the assignor listbox
                selected_index_assignor = selected_indices_assignor[0]  # Get the first selected index for Assignor data
                item_text_assignor = self.assignor_listbox.get(selected_index_assignor)  # Get the text of the selected item

                key_to_edit_assignor, _ = item_text_assignor.split(": ")  # Extract the key to edit for Assignor data

                # Open the edit window with existing key and value for editing for Assignor data
                self.open_edit_window(key=key_to_edit_assignor, value=self.assignor_data[key_to_edit_assignor])
        else:
            print("No item selected for editing.")

    def open_edit_window(self, key="", value=""):
        self.edit_window = tk.Toplevel(self.master)
        self.edit_window.title("Edit Key and Value")
        key_label = ttk.Label(self.edit_window, text="Key:")
        key_label.grid(row=0, column=0, padx=10, pady=10)
        self.key_entry = ttk.Entry(self.edit_window, width=30)
        self.key_entry.grid(row=0, column=1, padx=10, pady=10)
        self.key_entry.insert(0, key)

        value_label = ttk.Label(self.edit_window, text="Value:")
        value_label.grid(row=1, column=0, padx=10, pady=10)
        self.value_entry = ttk.Entry(self.edit_window, width=30)
        self.value_entry.grid(row=1, column=1, padx=10, pady=10)
        self.value_entry.insert(0, value)  # Insert existing value

        save_button = ttk.Button(self.edit_window, text="Save", command=self.save_edited_key_value)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)  # Might need adjusting

    def refresh_task_listbox(self):
        self.task_listbox.delete(0, tk.END)  # Clear the existing listbox
        self.populate_listbox(self.task_listbox, self.task_data)  # Populate listbox with updated data

    def refresh_staff_listbox(self):
        self.staff_listbox.delete(0, tk.END)  # Clear the existing staff listbox
        self.populate_listbox(self.staff_listbox, self.staff_data)  # Populate staff listbox with updated data

    def refresh_assignor_listbox(self):
        self.assignor_listbox.delete(0, tk.END)  # Clear the existing assignor listbox
        self.populate_listbox(self.assignor_listbox, self.assignor_data)  # Populate assignor listbox with updated data

    def save_edited_key_value(self):
        edited_key = self.key_entry.get().strip()
        edited_value = self.value_entry.get().strip()
        print("Edited Key:", edited_key)

        # Check if both key and value are provided
        if edited_key and edited_value:
            current_tab_index = self.tabControl.index(self.tabControl.select())
            if current_tab_index == 0:  # Task tab selected
                data_to_edit = self.task_data
                save_method = self.save_task_data
                refresh_method = self.refresh_task_listbox
                data_name = "Task"
            elif current_tab_index == 1:  # Staff tab selected
                data_to_edit = self.staff_data
                save_method = self.save_staff_data
                refresh_method = self.refresh_staff_listbox
                data_name = "Staff"
                try:
                    edited_key = int(edited_key)
                except ValueError:
                    print("Invalid key format. Key must be an integer.")
                    return
            elif current_tab_index == 2:  # Assignor tab selected
                data_to_edit = self.assignor_data
                save_method = self.save_assignor_data
                refresh_method = self.refresh_assignor_listbox
                data_name = "Assignor"
            else:
                print("Invalid tab selection.")
                return

            # Check if the edited key exists in the data dictionary
            if edited_key in data_to_edit:
                # Update the value based on the data structure
                data_to_edit[edited_key] = edited_value.split(',')  # Adjust split logic as needed

                # Save the edited data and refresh the listbox display
                save_method()
                print(f"Key '{edited_key}' edited with value '{edited_value}' in {data_name} data.")
                refresh_method()
                self.edit_window.destroy()  # Close the edit window
            else:
                print(f"Key '{edited_key}' not found in {data_name} data.")
        else:
            print("Please provide both key and value.")

    def refresh_input_boxes(self):
        # Clear existing listboxes and recreate them with updated data
        if self.tabControl.index(self.tabControl.select()) == 0:  # Check if Task tab is selected
            for child in self.tab_task.winfo_children():
                child.destroy()
            self.create_input_boxes(self.tab_task, self.task_data)
        elif self.tabControl.index(self.tabControl.select()) == 1:  # Check if Staff tab is selected
            for child in self.tab_staff.winfo_children():
                child.destroy()
            self.create_input_boxes(self.tab_staff, self.staff_data, is_staff=True, is_task=True)


def main():
    root = tk.Tk()
    app = SettingsApp(root)  # Pass the root window as an argument

    # Set the icon for the GUI window
    icon_path = Path(__file__).resolve().parent / 'data' / 'icon.ico'
    root.iconbitmap(icon_path)

    root.mainloop()


if __name__ == "__main__":
    main()