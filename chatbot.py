import json, random, pickle, numpy as np, nltk, threading
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
import tkinter as tk
from tkinter import scrolledtext, Frame, Entry, Button

# Setup
lemmatizer = WordNetLemmatizer()
model = load_model("chatbot_model.h5")
words = pickle.load(open("words.pkl", "rb"))
classes = pickle.load(open("classes.pkl", "rb"))
with open("intents.json") as file:
    intents = json.load(file)


# Functions
def clean_up_sentence(sentence):
    return [lemmatizer.lemmatize(word.lower()) for word in nltk.word_tokenize(sentence)]


def bow(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    return np.array([1 if w in sentence_words else 0 for w in words])


def predict_class(sentence):
    p = bow(sentence, words)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]


def get_response(ints):
    if not ints: return "Sorry, I didn't understand that."
    tag = ints[0]['intent']
    for i in intents['intents']:
        if i['tag'] == tag:
            return random.choice(i['responses'])
    return "Sorry, I didn't understand that."


# GUI
class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chatbot")
        self.root.geometry("500x600")
        self.root.configure(bg="#e5ddd5")

        # Scrollable chat area
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#ffffff", font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10, fill="both", expand=True)
        self.chat_area.config(state='disabled')

        # Entry frame
        entry_frame = Frame(root, bg="#e5ddd5")
        entry_frame.pack(fill="x", padx=10, pady=10)

        self.entry_box = Entry(entry_frame, font=("Arial", 14))
        self.entry_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_box.focus()
        self.entry_box.bind("<Return>", self.send_message)

        self.send_button = Button(entry_frame, text="Send", command=self.send_message, bg="#128C7E", fg="white",
                                  font=("Arial", 12))
        self.send_button.pack(side="right")

        # Minimum targets
        self.greetings_done = False
        self.products_done = False
        self.prices_done = False
        self.goodbye_done = False

        # Welcome message
        self.display_message("Bot", "Hello! I am your AI assistant. Say Hi to start chatting.")

    def display_message(self, sender, message):
        self.chat_area.config(state="normal")
        if sender == "You":
            self.chat_area.insert(tk.END, f"{sender}: {message}\n", "user")
        else:
            self.chat_area.insert(tk.END, f"{sender}: {message}\n", "bot")
        self.chat_area.tag_config("user", foreground="white", background="#128C7E", justify="right")
        self.chat_area.tag_config("bot", foreground="black", background="#DCF8C6", justify="left")
        self.chat_area.config(state="disabled")
        self.chat_area.yview(tk.END)

    def send_message(self, event=None):
        user_msg = self.entry_box.get().strip()
        if not user_msg: return
        self.display_message("You", user_msg)
        self.entry_box.delete(0, tk.END)
        # Run model in separate thread
        threading.Thread(target=self.process_response, args=(user_msg,)).start()

    def process_response(self, user_msg):
        ints = predict_class(user_msg)
        res = get_response(ints)
        self.display_message("Bot", res)


# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()