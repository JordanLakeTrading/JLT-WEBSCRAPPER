import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, scrolledtext, Canvas
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import threading
from nltk.corpus import wordnet as wn
from sklearn.feature_extraction.text import TfidfVectorizer

class StockScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Text Manipulation Tool")
        self.text_content = ""  # Variable to store all text
        self.chunk_size = 5000  # Display 5000 characters at a time
        self.current_position = 0  # Current starting index of text to display

        self.setup_frames()
        self.setup_buttons()
        self.setup_text_display()
        self.setup_icon()

    def setup_frames(self):
        self.left_frame = tk.Frame(self.root, width=200, relief=tk.RAISED, borderwidth=2, bg='white')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.right_frame = tk.Frame(self.root, bg='white')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def setup_buttons(self):
        tk.Label(self.left_frame, text="Enter URL or Select File:", bg='white').pack(fill=tk.X, padx=5)
        self.url_entry = tk.Entry(self.left_frame, width=20)
        self.url_entry.pack(fill=tk.X, padx=5)
        self.add_buttons()

    def add_buttons(self):
        commands = [("Load URL", self.load_from_url), ("Select File", self.load_from_file),
                    ("Batch Process URLs", self.process_url_list), ("Find and Replace", self.find_replace),
                    ("Highlight Text", self.highlight_text), ("Unhighlight Text", self.unhighlight_text),
                    ("Select HTML Elements", self.select_html_elements), ("Auto-Detect Tables", self.auto_detect_tables),
                    ("Sentiment Analysis", self.perform_sentiment_analysis), ("Display Words", self.display_words)]
        for (text, command) in commands:
            tk.Button(self.left_frame, text=text, command=command, bg='red', fg='white').pack(fill=tk.X, padx=5, pady=5)


    def setup_text_display(self):
        self.text = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, bg='black', fg='white')
        self.text.pack(fill=tk.BOTH, expand=True)

    def setup_icon(self):
        canvas = Canvas(self.left_frame, width=20, height=20, bg='white', highlightthickness=0)
        canvas.pack(side=tk.BOTTOM, pady=10, expand=True)

    def load_from_url(self):
        url = self.url_entry.get()
        threading.Thread(target=self.fetch_and_display_url, args=(url,)).start()

    def load_from_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            threading.Thread(target=self.read_file, args=(file_path,)).start()

    def fetch_and_display_url(self, url):
        try:
            response = requests.get(url)
            self.text_content = response.text  
            self.current_position = 0  
            self.update_text_display()  
            self.perform_sentiment_analysis()  
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to load URL: {e}")

    def read_file(self, file_path):
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                self.text_content = df.to_string()  
                self.current_position = 0  
                self.update_text_display()  
            else:
                with open(file_path, 'r') as file:
                    self.text_content = file.read()  
                    self.current_position = 0  
                    self.update_text_display()  
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def process_url_list(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            urls = pd.read_csv(file_path)
            for url in urls.itertuples():
                self.text.insert(tk.END, f"\nProcessing {url[1]}\n")
                threading.Thread(target=self.fetch_and_display_url, args=(url[1],)).start()

    def auto_detect_tables_from_content(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        tables = soup.find_all('table')
        for idx, table in enumerate(tables):
            df = pd.read_html(str(table))[0]
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                     filetypes=[("CSV files", "*.csv")],
                                                     initialfile=f"table_{idx}.csv")
            if file_path:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Table {idx} saved as {file_path}")

    def auto_detect_tables(self):
        content = self.text.get(1.0, tk.END)
        self.auto_detect_tables_from_content(content)

    def find_replace(self):
        find_str = simpledialog.askstring("Find", "Enter text to find:")
        replace_str = simpledialog.askstring("Replace", "Enter text to replace:")
        content = self.text.get(1.0, tk.END)
        new_content = content.replace(find_str, replace_str)
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, new_content)

    def highlight_text(self):
        target = simpledialog.askstring("Highlight", "Enter text to highlight:")
        start = 1.0
        while True:
            start = self.text.search(target, start, stopindex=tk.END)
            if not start:
                break
            end = f"{start}+{len(target)}c"
            self.text.tag_add('highlight', start, end)
            self.text.tag_configure('highlight', background='yellow')
            start = end

    def unhighlight_text(self):
        self.text.tag_remove('highlight', "1.0", tk.END)

    def select_html_elements(self):
        tag = simpledialog.askstring("Select HTML Elements", "Enter HTML tag to select (e.g., table):")
        content = self.text.get(1.0, tk.END)
        soup = BeautifulSoup(content, 'html.parser')
        elements = soup.find_all(tag)
        selected_text = '\n'.join(str(element) for element in elements)
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, selected_text)
    
    def show_next_chunk(self):
        if self.current_position + self.chunk_size < len(self.text_content):
            self.current_position += self.chunk_size
            self.update_text_display()

    def show_previous_chunk(self):
        if self.current_position - self.chunk_size >= 0:
            self.current_position -= self.chunk_size
        else:
            self.current_position = 0
        self.update_text_display()

    def update_text_display(self):
        self.text.delete(1.0, tk.END)
        end_pos = min(self.current_position + self.chunk_size, len(self.text_content))
        display_text = self.text_content[self.current_position:end_pos]
        self.text.insert(tk.END, display_text)

    def perform_sentiment_analysis(self):
        if not self.text_content:
            messagebox.showerror("Error", "No content loaded. Please load a URL or file first.")
            return

        positive_words = []
        negative_words = []

        for word in self.word_list:
            synsets = wn.synsets(word)
            if any(syn.pos() == 'a' for syn in synsets):
                if self.is_positive_adjective(word):
                    positive_words.append(word)
                else:
                    negative_words.append(word)

        positive_df = pd.DataFrame(positive_words, columns=['Word'])
        negative_df = pd.DataFrame(negative_words, columns=['Word'])

        positive_df['Frequency'] = positive_df['Word'].map(positive_df['Word'].value_counts())
        negative_df['Frequency'] = negative_df['Word'].map(negative_df['Word'].value_counts())

        positive_output = "Positive Words:\n" + positive_df.to_string(index=False)
        negative_output = "\nNegative Words:\n" + negative_df.to_string(index=False)

        # Create a new window
        sentiment_window = tk.Toplevel()
        sentiment_window.title("Sentiment Analysis Results")
        
        # Create text widget to display results
        results_text = tk.Text(sentiment_window)
        results_text.insert(tk.END, positive_output + "\n" + negative_output)
        results_text.pack()

        sentiment_window.mainloop()

    
    
    def is_positive_adjective(self, word):
        synsets = wn.synsets(word, pos=wn.ADJ)
        for synset in synsets:
            if synset.positive_score() > synset.negative_score():
                return True
        return False
    
    def display_words(self):
        try:
            if self.text_content:
                # Get the webpage text content
                soup = BeautifulSoup(self.text_content, 'html.parser')
                webpage_text = soup.get_text()

                # Split the text into words
                self.word_list = re.findall(r'\w+', webpage_text)

                # Create a new window to display the words
                display_window = tk.Toplevel(self.root)
                display_window.title("Words from URL")
                text_box = scrolledtext.ScrolledText(display_window, wrap=tk.WORD)

                # Insert the words into the text box
                word_list_str = '\n'.join(self.word_list)
                text_box.insert(tk.END, word_list_str)
                text_box.pack(fill=tk.BOTH, expand=True)
            else:
                messagebox.showerror("Error", "No content loaded. Please load a URL first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        
root = tk.Tk()
app = StockScraperApp(root)
root.mainloop()
