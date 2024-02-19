from bs4 import BeautifulSoup
import requests
import tkinter as tk
import sqlite3

connection = sqlite3.connect("my_dictionary")

cur = connection.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS my_dict (id INTEGER PRIMARY KEY, 
eng_word TEXT, translation TEXT, lbl_name TEXT, btn_name TEXT)""")


class Root:
    def __init__(self):
        self.root = tk.Tk()
        self.root.tk_setPalette(background='white')
        self.root.geometry("800x500")
        self.root.title("my_english_dictionary")

        self.translation_list = []
        self.note_list = []

        # gui elements
        self.frame_left = tk.Frame(self.root, height=250)
        self.frame_left_child = tk.Frame(self.frame_left, width=200, height=250)

        self.frame_right = tk.Frame(self.root, width=360, height=500)

        self.entry_word = tk.Entry(self.frame_left, bg='#F3F3F3', font=('Calibri', 12))
        self.translate_btn = tk.Button(self.frame_left, text="translate", bg='Gold', font=('Calibri', 11),
                                       command=self.translate)
        self.add_btn = tk.Button(self.frame_left, text="add it >>>", bg='YellowGreen', font=('Calibri', 11),
                                 command=lambda: self.add_word(self.entry_word.get(), self.translation_list))
        self.show_btn = tk.Button(self.frame_left, text="show", font=('Calibri', 11), command=self.get_dict)

        # grid
        self.frame_left.grid(column=0, row=0, sticky='nw')
        self.frame_left_child.grid(column=0, row=2, sticky='nw', pady=10)
        self.frame_right.grid(column=0, row=0, sticky='e', padx=430)
        self.entry_word.grid(column=0, row=0, padx=10, pady=10, sticky='w')
        self.translate_btn.grid(column=0, row=0, padx=180, sticky='w')

        self.get_dict()
        self.root.mainloop()

    def delete_word(self, idd):
        cur.execute("""DELETE FROM my_dict WHERE id=?""", (idd,))

        for label in self.frame_right.winfo_children():
            label.destroy()

        connection.commit()

        self.get_dict()

    def add_word(self, eng_word, translation):
        count = cur.execute("""SELECT COUNT(*) FROM my_dict""")
        result = count.fetchone()

        if result[0] > 9:
            for label in self.frame_left_child.winfo_children():
                label.destroy()
            self.create_left_label(self.frame_left_child, 'max 10 words to learn')
        else:

            cur.execute("""INSERT INTO my_dict (eng_word, translation) VALUES (?, ?)""",
                        (eng_word, str(translation)))

            connection.commit()
            # self.note_list.append(eng_word)
            self.get_dict()

    def get_dict(self):
        cur.execute("""SELECT * FROM my_dict""")
        result = cur.fetchall()

        for res in result:
            self.create_word_note(self.frame_right, str(res[1]) + ' ' + str(res[2]), str(res[0]))

    def translate(self):

        self.translation_list = []

        query = self.entry_word.get()
        page = requests.get(f'https://www.diki.pl/slownik-angielskiego?q={query}')
        soup = BeautifulSoup(page.content, 'html.parser')

        tags = soup.find_all("li", limit=3)

        for tag in tags:
            spans = tag.find_all("span", {"class": "hw"})

            for span in spans:
                self.translation_list.append(span.text)

        for label in self.frame_left_child.winfo_children():
            label.destroy()

        for i in range(len(self.translation_list)):
            self.create_left_label(self.frame_left_child, self.translation_list[i], 0, i + 2)

        self.add_btn.grid(column=0, row=1, padx=10, sticky='w')

    def create_word_note(self, frame_right, text, row):
        lbl_name = tk.Label(frame_right, padx=10, text=text, wraplength=325, font=('Calibri', 11))
        btn_name = tk.Button(frame_right, text='x', padx=10, fg='maroon', font=('Calibri', 9),
                             command=lambda: self.delete_word(str(row)))
        lbl_name.grid(column=1, row=row, sticky='nw')
        btn_name.grid(column=0, row=row, sticky='nw')

    def create_left_label(self, frame_pos, word, col=0, row=0):
        self.word = tk.Label(frame_pos)
        self.word.config(text=word)
        self.word.update()
        self.word.grid(column=col, row=row, padx=10, sticky='w')


Root()
