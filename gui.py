import tkinter as tk
import customtkinter
import math
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
        # Configure window
        self.title("Strom AI Assistant")
        self.geometry("1000x700")
        
        # Configure grid weight
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Fonts
        self.font_bold = customtkinter.CTkFont(size=14, weight="bold")
        self.font_msg = customtkinter.CTkFont(size=13)

        # Sidebar (Left)
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # Logo Canvas for Procedural Animation
        # Using a fixed background color that matches standard Dark mode CTkFrame
        # Note: Ideally we'd fetch the exact theme color, but #2B2B2B is the standard dark gray.
        self.logo_canvas = tk.Canvas(self.sidebar_frame, width=140, height=140, bg="#2B2B2B", highlightthickness=0)
        self.logo_canvas.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Animation State
        self.anim_phase = 0
        self.animation_running = True
        self._animate_orb()
        
        self.status_label = customtkinter.CTkLabel(self.sidebar_frame, text="Status: Offline", text_color="gray")
        self.status_label.grid(row=1, column=0, padx=20, pady=10)
        
        self.start_button = customtkinter.CTkButton(self.sidebar_frame, text="Start Listening", command=self.start_listening)
        self.start_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.stop_button = customtkinter.CTkButton(self.sidebar_frame, text="Stop", command=self.stop_listening, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.stop_button.grid(row=3, column=0, padx=20, pady=10)

        # Chat Area (Right)
        # Chat Area (Right)
        self.chat_frame = customtkinter.CTkScrollableFrame(self, label_text="Conversation", label_font=self.font_bold)
        self.chat_frame.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="nsew")
        
        # Input Area (Bottom Right)
        self.input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
        
        self.entry = customtkinter.CTkEntry(self.input_frame, placeholder_text="Type your message...")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.send_text)
        
        self.send_button = customtkinter.CTkButton(self.input_frame, text="Send", width=100, command=self.send_text)
        self.send_button.pack(side="right")
        
        # Typing Indicator State
        self.typing_label = None
        self.typing_running = False
        
        # Strom Instance
        self.strom = None
        self.strom_thread = None
        self.is_running = False

        # Auto-initialize on start
        self.after(100, self.init_strom_async)

    def init_strom_async(self):
        """Initialize Strom: Text first (fast), then Voice (slow)."""
        # 1. Initialize Text Core (Fast) - Run on Main Thread for TTS safety
        self._init_text_core_main()
        
        # 2. Trigger Voice Load (Slow) - Run in Background
        threading.Thread(target=self._load_voice_background, daemon=True).start()
    
    def _init_text_core_main(self):
        self.status_label.configure(text="Status: Init Core...", text_color="orange")
        try:
            # 1. Initialize Text Core (Fast)
            self.strom = StromAssistant()
            
            # Register callbacks immediately
            self.strom.on_status_change = self.update_status
            self.strom.on_user_input = self.add_user_message
            self.strom.on_assistant_response = self.add_strom_message
            
            self.status_label.configure(text="Status: Text Ready (Loading Voice...)", text_color="yellow")
            self.add_strom_message("Text core ready. Loading voice models...")
            
            # 2. Trigger Voice Load (Slow) -> Handled by separate thread call
            # threading.Thread(target=self._load_voice_background, daemon=True).start()

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
            print(f"[GUI] Init failed: {e}")

    def _load_voice_background(self):
        """Load voice components in background."""
        try:
            if self.strom:
                 self.strom.initialize_voice_core()
                 
                 if self.strom.is_voice_available:
                     self.status_label.configure(text="Status: Ready (Voice+Text)", text_color="green")
                     self.start_button.configure(state="normal", text="Start Listening")
                     self.add_strom_message("Voice systems online.")
                 else:
                     self.status_label.configure(text="Status: Text Only (Voice Failed)", text_color="orange")
                     self.start_button.configure(state="disabled", text="Voice Unavailable")
                     self.add_strom_message("Voice failed to load. Text only.")
        except Exception as e:
            print(f"[GUI] Background voice load error: {e}")

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
             self.add_strom_message("System initializing... please wait.")
             return

        try:
            self.status_label.configure(text="Status: Processing...", text_color="blue")
            
            # Show Typing Indicator
            self.show_typing_indicator()
            
            # Use the process method directly
            print(f"[GUI] Calling strom.process({text})")
            response = self.strom.process(text)
            print(f"[GUI] Response: {response}")
            
            # Hide Typing
            self.hide_typing_indicator()
            
            # self.add_strom_message(response) # Removed because callback handles it?
            # WAIT: If callback handles it, we get double messages?
            # Let's check init: self.strom.on_assistant_response = self.add_strom_message
            # Strom.process calls self.conv_manager.add_exchange -> NO, it returns response.
            # Strom.speak calls on_assistant_response.
            
            self.strom.speak(response)
            
            if self.is_running and self.strom.is_voice_available:
                 self.update_status("Listening...")
            elif self.strom.is_voice_available:
                 self.update_status("Standing by")
            else:
                 self.status_label.configure(text="Status: Text Only Mode", text_color="yellow")
                 
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
            
            if self.strom.is_voice_available:
                self.update_status("Standing by")
            else:
                self.update_status("Text Only Mode")
                return
            
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
        msg_frame = customtkinter.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_frame.pack(pady=5, padx=10, fill="x")
        
        # Spacer to push to right
        customtkinter.CTkLabel(msg_frame, text="", width=50).pack(side="left", fill="x", expand=True)
        
        lbl = customtkinter.CTkLabel(
            msg_frame, 
            text=text, 
            anchor="e", 
            justify="right", 
            fg_color="#1F6AA5", # Accent color
            text_color="white",
            corner_radius=15,
            wraplength=400,
            padx=15,
            pady=10,
            font=self.font_msg
        )
        lbl.pack(side="right", anchor="e")
        
        # Scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)

        # Scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def add_strom_message(self, text, animate=True):
        msg_frame = customtkinter.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_frame.pack(pady=5, padx=10, fill="x")
        
        lbl = customtkinter.CTkLabel(
            msg_frame, 
            text="", # Start empty for animation
            anchor="w", 
            justify="left", 
            fg_color="#333333", 
            text_color="white",
            corner_radius=15,
            wraplength=400,
            padx=15,
            pady=10,
            font=self.font_msg
        )
        lbl.pack(side="left", anchor="w")
        
        # Spacer
        customtkinter.CTkLabel(msg_frame, text="", width=50).pack(side="right", fill="x", expand=True)

        # Scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)

        if animate:
            self._typewriter_effect(lbl, text, 0)
        else:
            lbl.configure(text=text)

    def _typewriter_effect(self, label, text, index):
        """Reveal text character by character."""
        if index < len(text):
            current_text = text[:index+1]
            label.configure(text=current_text)
            
            # Scroll to keep bottom visible during typing
            if index % 5 == 0:
                self.chat_frame._parent_canvas.yview_moveto(1.0)
                
            # Speed: 10ms - 30ms random? Or fixed 20ms for smoothness
            self.after(20, self._typewriter_effect, label, text, index + 1)

    def show_typing_indicator(self):
        """Show animated typing bubble."""
        if self.typing_label:
            return
            
        msg_frame = customtkinter.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_frame.pack(pady=5, padx=10, fill="x")
        
        self.typing_label = customtkinter.CTkLabel(
            msg_frame, 
            text="...", 
            anchor="w", 
            justify="left", 
            fg_color="#333333", 
            text_color="gray",
            corner_radius=15,
            padx=15,
            pady=10,
            font=self.font_msg
        )
        self.typing_label.pack(side="left", anchor="w")
        
        # Save reference to frame to destroy it later? 
        # Actually easier to just keep label ref and destroy parent
        self.typing_label.frame_ref = msg_frame
        
        self.typing_running = True
        self._animate_typing(0)
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def hide_typing_indicator(self):
        """Remove typing bubble."""
        self.typing_running = False
        if self.typing_label:
            self.typing_label.frame_ref.destroy()
            self.typing_label = None

    def _animate_typing(self, step):
        """Animate the dots ..."""
        if not self.typing_running or not self.typing_label:
            return
            
        dots = "." * ((step % 3) + 1)
        self.typing_label.configure(text=dots)
        self.after(300, self._animate_typing, step + 1)

    def _animate_orb(self):
        """Draw a procedural pulsing orb animation."""
        if not self.animation_running:
            return
            
        self.logo_canvas.delete("all")
        
        w, h = 140, 140
        cx, cy = w/2, h/2
        
        # 1. Outer Ripples (2 rings)
        for i in range(2):
            # Phase shift for each ring
            local_phase = (self.anim_phase + i * math.pi) % (2 * math.pi)
            
            # Breathing func: 0.0 -> 1.0 -> 0.0
            scale = (math.sin(local_phase) + 1) / 2
            
            radius = 30 + (35 * scale) # 30 to 65
            
            # Color interpolation: Blue (#1F6AA5) to Cyan/Transparent?
            # Simpler: Toggle colors or opacity by stippling (if supported) or just width/color
            # We'll stick to solid lines for "vector" look
            
            color = "#1F6AA5" # Brand blue
            # Width varies with expansion
            width = 3 * (1 - scale) + 1
            
            self.logo_canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, outline=color, width=width)

        # 2. Central Core
        # Pulsing center
        core_scale = (math.sin(self.anim_phase * 2) + 1) / 2 # Faster pulse
        core_r = 20 + (5 * core_scale)
        self.logo_canvas.create_oval(cx-core_r, cy-core_r, cx+core_r, cy+core_r, fill="#1F6AA5", outline="")
        
        # 3. Inner "Eye" or Highlght
        eye_r = 8
        self.logo_canvas.create_oval(cx-eye_r, cy-eye_r, cx+eye_r, cy+eye_r, fill="white", outline="")

        # Update Phase
        self.anim_phase += 0.05
        
        # ~30 FPS
        self.after(33, self._animate_orb)

if __name__ == "__main__":
    app = StromGUI()
    app.mainloop()
