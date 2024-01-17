import customtkinter as ctk
import tkinter as tk

# Function to create the application window
def create_app_window():
    # Create a root window
    root = ctk.CTk()
    root.title("CustomTkinter Window")

    # Set window size to 1600x900 and disable resizing
    root.geometry("1600x900")
    root.resizable(False, False)

    # Create a frame for organization and use grid layout
    frame = ctk.CTkFrame(master=root)
    frame.place(relwidth=1, relheight=1)  # Make the frame fill the entire root window

    # Create and place the 'Symbol' label and dropdown box
    symbol_label = ctk.CTkLabel(master=frame, text="Symbol")
    symbol_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    symbol_dropdown = ctk.CTkComboBox(master=frame, values=["Option 1", "Option 2", "Option 3"])
    symbol_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    # Create and place the 'Strategy' label and dropdown box
    strategy_label = ctk.CTkLabel(master=frame, text="Strategy")
    strategy_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    strategy_dropdown = ctk.CTkComboBox(master=frame, values=["Strategy 1", "Strategy 2", "Strategy 3"])
    strategy_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    # Create and place the date inputs
    date_label_1 = ctk.CTkLabel(master=frame, text="Start Date")
    date_label_1.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    date_entry_1 = ctk.CTkEntry(master=frame)
    date_entry_1.grid(row=2, column=1, padx=10, pady=10, sticky="w")
    date_entry_1.insert(0, "YYYY-MM-DD")

    date_label_2 = ctk.CTkLabel(master=frame, text="End Date")
    date_label_2.grid(row=3, column=0, padx=10, pady=10, sticky="w")
    date_entry_2 = ctk.CTkEntry(master=frame)
    date_entry_2.grid(row=3, column=1, padx=10, pady=10, sticky="w")
    date_entry_2.insert(0, "YYYY-MM-DD")

    # Start the application
    root.mainloop()

# Run the application
create_app_window()
