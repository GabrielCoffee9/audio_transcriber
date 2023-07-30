import customtkinter as ctk
import tkinter as tk
import backend
import threading
import frontend_helper

root = tk.Tk()

text_live_transcribe = ctk.StringVar()

root.title('Audio transcriber')
root.attributes('-transparentcolor', 'red')

root.config(bg='#112A4A')

optionmenu_var = ctk.StringVar(value="pt-BR")  


def clear_root():
    for widget in root.winfo_children():
        print(widget)
        widget.destroy()


def live_transcribe():
    
    root.attributes('-topmost', True)
    root.attributes('-fullscreen', True)
    root.config(bg = 'red')
    root.update()

    clear_root()

    ctk.CTkButton(root, text="Sair", command=root.destroy).pack(expand = True,anchor='se')

    main_live_transcribe = ctk.CTkLabel(root, textvariable=text_live_transcribe, bg_color='red')

    main_live_transcribe.pack(side='bottom', pady= 50)

    main_live_transcribe.configure(fg_color="yellow", text_color="#000000", font=("Arial", 26), wraplength=900)
    main_live_transcribe.pack()

    while True:
        try:
            for transcribe in backend.transcribe_streaming_v2(optionmenu_var.get()):    
                text_live_transcribe.set(transcribe)
                root.update()
        except Exception as e:
                    print("cancelado. {e}")
    
def start_live_transcribe():
    thread_generator = threading.Thread(target=live_transcribe)
    thread_generator.daemon = True
    thread_generator.start()



def offline_transcribe(): 
    frameLoading = ctk.CTkFrame(root)
    label_progress_bar = ctk.CTkLabel(frameLoading, text='Realizando transcrição...')
    label_progress_bar.pack()

    transcribe_progress_bar = ctk.CTkProgressBar(frameLoading,width=60, mode='indeterminate')
    transcribe_progress_bar.start()
    transcribe_progress_bar.pack()

    frameLoading.pack(expand=True, fill="both")
    root.update()

    backend.offline_file_transcribe()
        
    frameLoading.pack_forget()
    root.update()

live_transcription_button = ctk.CTkButton(root, text="Transcrição ao vivo (requer internet)", command = start_live_transcribe)
live_transcription_button.pack(expand=True)

ctk.CTkOptionMenu(master=root,values=["pt-BR", "en-US"], variable=optionmenu_var).pack()

offline_transcription_button = ctk.CTkButton(root, text="Transcrição de arquivo (offline) - english only", command = offline_transcribe)
offline_transcription_button.pack(expand=True)

ctk.CTkButton(root, text="Sair", command=root.destroy).pack(expand=True)

frontend_helper.center_window(root,800, 600)
root.mainloop()



