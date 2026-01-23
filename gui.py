import customtkinter
import threading
import sys
from main import StromAssistant
import time

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class StromGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Strom AI Assistant")
        self.geometry("800x600")
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (Left)
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Strom AI", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.status_label = customtkinter.CTkLabel(self.sidebar_frame, text="Status: Offline", text_color="gray")
        self.status_label.grid(row=1, column=0, padx=20, pady=10)
        
        self.start_button = customtkinter.CTkButton(self.sidebar_frame, text="Start Listening", command=self.start_listening)
        self.start_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.stop_button = customtkinter.CTkButton(self.sidebar_frame, text="Stop", command=self.stop_listening, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.stop_button.grid(row=3, column=0, padx=20, pady=10)

        # Chat Area (Right)
        self.chat_frame = customtkinter.CTkScrollableFrame(self, label_text="Conversation")
        self.chat_frame.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="nsew")
        
        # Input Area (Bottom Right)
        self.input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
        
        self.entry = customtkinter.CTkEntry(self.input_frame, placeholder_text="Type your message...")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.send_text)
        
        self.send_button = customtkinter.CTkButton(self.input_frame, text="Send", width=100, command=self.send_text)
        self.send_button.pack(side="right")
        
        # Strom Instance
        self.strom = None
        self.strom_thread = None
        self.is_running = False

    def send_text(self, event=None):
        text = self.entry.get()
        if not text.strip():
            return
            
        self.entry.delete(0, "end")
        self.add_user_message(text)
        
        # Process in thread
        print(f"[GUI] Processing text: {text}")
        threading.Thread(target=self.process_text_thread, args=(text,)).start()

    def process_text_thread(self, text):
        print(f"[GUI] Thread started for: {text}")
        if not self.strom:
            print("[GUI] Initializing Strom...")
            self.status_label.configure(text="Status: Initializing...", text_color="orange")
            try:
                self.strom = StromAssistant()
                print("[GUI] Strom initialized")
                # Register callbacks
                self.strom.on_status_change = self.update_status
                # on_user_input and on_assistant_response handled manually for text input
                self.update_status("Standing by")
            except Exception as e:
                print(f"[GUI] Init error: {str(e)}")
                self.update_status(f"Error: {str(e)}")
                return

        try:
            self.status_label.configure(text="Status: Processing...", text_color="blue")
            
            # Use the process method directly
            print(f"[GUI] Calling strom.process({text})")
            response = self.strom.process(text)
            print(f"[GUI] Response: {response}")
            
            self.add_strom_message(response)
            self.strom.speak(response)
            
            if self.is_running:
                 self.update_status("Listening...")
            else:
                 self.update_status("Standing by")
                 
        except Exception as e:
            print(f"[GUI] Process error: {str(e)}")
            self.add_strom_message(f"Error: {str(e)}")
            self.update_status("Error")

    def start_listening(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.status_label.configure(text="Status: Starting...", text_color="orange")
        self.start_button.configure(state="disabled")
        
        # Initialize Strom in a separate thread if not already
        self.strom_thread = threading.Thread(target=self.run_strom)
        self.strom_thread.daemon = True
        self.strom_thread.start()

    def stop_listening(self):
        if not self.is_running:
            return
            
        self.is_running = False
        if self.strom:
            self.strom.is_running = False
        
        self.status_label.configure(text="Status: Stopping...", text_color="red")
        self.start_button.configure(state="normal")

    def run_strom(self):
        try:
            if not self.strom:
                self.strom = StromAssistant()
                
            # Register callbacks
            self.strom.on_status_change = self.update_status
            self.strom.on_user_input = self.add_user_message
            self.strom.on_assistant_response = self.add_strom_message
            
            self.update_status("Standing by")
            
            # Enable running flag again for re-start
            self.strom.is_running = True
            
            # Run Strom main loop
            self.strom.run()
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.is_running = False
            self.update_status("Offline")
            self.start_button.configure(state="normal", text="Start Listening")

    def update_status(self, status):
        # Update UI thread safe
        color = "green" if "Listening" in status else "gray"
        self.status_label.configure(text=f"Status: {status}", text_color=color)

    def add_user_message(self, text):
        msg = customtkinter.CTkLabel(self.chat_frame, text=f"You: {text}", anchor="e", justify="right", fg_color=("gray85", "gray25"), corner_radius=10)
        msg.pack(pady=5, padx=10, anchor="e", fill="x")

    def add_strom_message(self, text):
        msg = customtkinter.CTkLabel(self.chat_frame, text=f"Strom: {text}", anchor="w", justify="left", fg_color=("gray75", "gray35"), corner_radius=10)
        msg.pack(pady=5, padx=10, anchor="w", fill="x")

if __name__ == "__main__":
    app = StromGUI()
    app.mainloop()
