import tkinter as tk
import backend
import threading

root = tk.Tk()

text_live_transcribe = tk.StringVar()

root.title('')

root.attributes('-transparentcolor', 'red')
root.attributes('-topmost', True)
root.attributes('-fullscreen', True)
root.config(bg='red')

def live_transcribe():
    main_live_transcribe.config(fg="yellow", bg="#8D9093", font=("Arial", 26), wraplength=900)
    main_live_transcribe.pack()
    for transcribe in backend.transcribe_streaming_v2():    
        text_live_transcribe.set(transcribe)
        root.update()

def start_live_transcribe():
    thread_generator = threading.Thread(target=live_transcribe)
    thread_generator.daemon = True
    thread_generator.start()


new_transcription_button = tk.Button(root, text="Transcrição ao vivo (requer internet)", command = start_live_transcribe)
new_transcription_button.pack(padx=10,pady=10)


close_button = tk.Button(root, text="Sair", command=root.destroy).pack(padx=100)

main_live_transcribe = tk.Label(root, textvariable=text_live_transcribe, bg='red')

main_live_transcribe.pack(side='bottom', pady= 50)

root.mainloop()



