import random, os, traceback, pickle
from collections import Counter
from sklearn.ensemble import RandomForestClassifier

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window

Window.clearcolor = (0.05, 0.2, 0.05, 1)  # Koyu yeşil arka plan

class EverydleApp(App):
    def build(self):
        self.title = "EVERYDLE"
        self.word_list_3, self.word_list_4, self.word_list_5, self.word_list_6, self.word_list_7 = [], [], [], [], []
        self.target = ""
        self.word_length = 5
        self.max_attempts = 6
        self.current_row = 0
        self.current_col = 0
        self.game_over = False
        self.cells = []
        self.key_buttons = {}
        self.username = ""
        self.load_word_lists()
        self.root = BoxLayout()
        self.root.add_widget(self.build_login_screen())
        return self.root

    # --- 1. Kullanıcı Girişi Ekranı ---
    def build_login_screen(self):
        layout = BoxLayout(orientation='vertical', padding=40, spacing=40)
        layout.add_widget(Label(
            text="EVERYDLE",
            font_size='40sp',
            bold=True,
            color=(0.0, 0.5, 0.0, 1),  # Koyu yeşil yazı
            size_hint_y=0.3
        ))
        layout.add_widget(Label(text="Kullanıcı Adı Giriniz:", font_size='28sp', color=(1,1,1,1), size_hint_y=0.2))
        self.username_input = TextInput(font_size='28sp', size_hint_y=0.2, multiline=False, halign='center', background_color=(0.2,0.2,0.2,1), foreground_color=(1,1,1,1))
        layout.add_widget(self.username_input)
        btn = Button(text="Giriş Yap", font_size='28sp', size_hint_y=0.2, background_color=(0.2,0.7,0.2,1), color=(1,1,1,1), on_press=self.on_login)
        layout.add_widget(btn)
        return layout

    def on_login(self, instance):
        username = self.username_input.text.strip()
        if not username:
            Popup(title="Hata", content=Label(text="Kullanıcı adı boş olamaz!", font_size='22sp'), size_hint=(0.7,0.3)).open()
            return
        self.username = username
        self.root.clear_widgets()
        self.root.add_widget(self.build_word_length_screen())

    # --- 2. Kelime Uzunluğu Seçim Ekranı ---
    def build_word_length_screen(self):
        layout = BoxLayout(orientation='vertical', padding=40, spacing=40)
        layout.add_widget(Label(text=f"Hoşgeldin, {self.username}!", font_size='32sp', color=(0.2,0.8,1,1), size_hint_y=0.2))
        layout.add_widget(Label(text="Kelime Uzunluğu Seçiniz:", font_size='28sp', color=(1,1,1,1), size_hint_y=0.2))
        btn_layout = BoxLayout(orientation='horizontal', spacing=30, size_hint_y=0.3)
        for length in [3, 4, 5, 6, 7]:
            btn = Button(
                text=f"{length} Harfli",
                font_size='32sp',
                size_hint=(0.2, 1),
                background_color=(0.3,0.3,0.8,1),
                color=(1,1,1,1),
                on_press=lambda x, l=length: self.start_game(l)
            )
            btn_layout.add_widget(btn)
        layout.add_widget(btn_layout)
        return layout

    # --- 3. Oyun Ekranı ---
    def start_game(self, word_length):
        self.word_length = word_length
        self.max_attempts = {3: 4, 4: 5, 5: 6, 6: 7, 7: 8}.get(word_length, 6)
        word_dict = {3: self.word_list_3, 4: self.word_list_4, 5: self.word_list_5, 6: self.word_list_6, 7: self.word_list_7}
        self.target = random.choice(word_dict.get(word_length, self.word_list_5))
        self.current_row = 0
        self.current_col = 0
        self.game_over = False
        self.cells = []
        self.key_buttons = {}

        root = BoxLayout(orientation='vertical', padding=30, spacing=30)
        root.add_widget(Label(
            text=f"EVERYDLE - {self.username}",
            font_size='32sp',
            color=(0.0, 0.5, 0.0, 1),  # Koyu yeşil yazı
            size_hint_y=0.15
        ))
        board = GridLayout(rows=self.max_attempts, cols=word_length, spacing=10, size_hint_y=0.5)
        for r in range(self.max_attempts):
            temp_row = []
            for c in range(word_length):
                btn = Button(
                    text="",
                    font_size='36sp',
                    background_normal='',
                    background_color=(0.15, 0.3, 0.15, 1),  # Koyu yeşil kutu
                    color=(1, 1, 1, 1),  # Beyaz harfler
                    size_hint=(1,1),
                    disabled=True
                )
                board.add_widget(btn)
                temp_row.append(btn)
            self.cells.append(temp_row)
        root.add_widget(board)

        keyboard_area = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.3)
        for row_letters, padding in [("QWERTYUIOP", 0), ("ASDFGHJKL", 40), ("ZXCVBNM", 0)]:
            row = BoxLayout(spacing=8, padding=[padding, 0, 0, 0] if padding else [0, 0, 0, 0])
            if row_letters == "ZXCVBNM":
                row.add_widget(Button(text="ENTER", font_size='26sp', background_color=(0.6, 0.6, 0.6, 1), color=(1,1,1,1), on_press=self.on_enter))
            for letter in row_letters:
                btn = Button(
                    text=letter,
                    font_size='26sp',
                    background_normal='',
                    background_color=(0.95, 0.95, 0.95, 1),
                    color=(0, 0, 0, 1),
                    on_press=self.on_key_press
                )
                self.key_buttons[letter] = btn
                row.add_widget(btn)
            if row_letters == "ZXCVBNM":
                row.add_widget(Button(text="DEL", font_size='26sp', background_color=(0.6, 0.6, 0.6, 1), color=(1,1,1,1), on_press=self.on_backspace))
            keyboard_area.add_widget(row)
        root.add_widget(keyboard_area)

        ai_button = Button(
            text="AI Tahmin Öner",
            size_hint_y=0.12,
            font_size='28sp',
            background_color=(0.2, 0.7, 0.2, 1),
            color=(1,1,1,1),
            on_press=self.on_ai_suggest
        )
        root.add_widget(ai_button)

        back_button = Button(
            text="Ana Menüye Dön",
            size_hint_y=0.12,
            font_size='28sp',
            background_color=(0.5, 0.5, 0.8, 1),
            color=(1,1,1,1),
            on_press=self.return_to_menu
        )
        root.add_widget(back_button)

        self.root.clear_widgets()
        self.root.add_widget(root)

    def return_to_menu(self, *args):
        self.root.clear_widgets()
        self.root.add_widget(self.build_word_length_screen())

    # --- AI Hybrid Model Methods ---
    def word_to_features(self, word):
        features = []
        for i in range(len(word)):
            vec = [0]*26
            vec[ord(word[i])-ord('A')] = 1
            features.extend(vec)
        counts = Counter(word)
        features.extend([counts.get(chr(ord('A')+i), 0) for i in range(26)])
        return features

    def train_or_load_rf(self, word_list):
        model_path = f"wordle_rf_model_{len(word_list[0])}.pkl"
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                rf = pickle.load(f)
        else:
            X = [self.word_to_features(w) for w in word_list]
            y = [sum(ord(c)-ord('A') for c in w) % 10 for w in word_list]  # Dummy target
            rf = RandomForestClassifier(n_estimators=50, n_jobs=-1)
            rf.fit(X, y)
            with open(model_path, "wb") as f:
                pickle.dump(rf, f)
        return rf

    def suggest_next_guess(self, rf, possible_words, prev_guesses):
        if not possible_words:
            return random.choice(possible_words)
        X = [self.word_to_features(w) for w in possible_words]
        preds = rf.predict_proba(X)
        rf_scores = [p[0] for p in preds]
        letter_counts = {}
        for word in possible_words:
            for c in set(word):
                letter_counts[c] = letter_counts.get(c, 0) + 1
        freq_scores = []
        for word in possible_words:
            score = sum(letter_counts.get(c, 0) for c in set(word))
            freq_scores.append(score)
        max_rf = max(rf_scores) if rf_scores else 1
        max_freq = max(freq_scores) if freq_scores else 1
        hybrid_scores = []
        for rf_score, freq_score in zip(rf_scores, freq_scores):
            norm_rf = rf_score / max_rf
            norm_freq = freq_score / max_freq
            hybrid_scores.append(0.6 * norm_rf + 0.4 * norm_freq)
        best_idx = max(range(len(possible_words)), key=lambda i: hybrid_scores[i])
        best_word = possible_words[best_idx]
        if best_word in prev_guesses:
            for i in sorted(range(len(possible_words)), key=lambda i: -hybrid_scores[i]):
                if possible_words[i] not in prev_guesses:
                    return possible_words[i]
            return random.choice(possible_words)
        return best_word

    def on_ai_suggest(self, instance):
        word_dict = {
            3: self.word_list_3,
            4: self.word_list_4,
            5: self.word_list_5,
            6: self.word_list_6,
            7: self.word_list_7
        }
        word_list = word_dict.get(self.word_length, self.word_list_5)
        rf = self.train_or_load_rf(word_list)
        prev_guesses = []
        for row in self.cells:
            guess = ''.join(btn.text for btn in row)
            if len(guess) == self.word_length and all(btn.text for btn in row):
                prev_guesses.append(guess)
        possible_words = [w for w in word_list if w not in prev_guesses]
        suggestion = self.suggest_next_guess(rf, possible_words, prev_guesses)
        Popup(title="AI Tahmini", content=Label(text=f"AI önerisi: {suggestion}", font_size='26sp'), size_hint=(0.7, 0.3)).open()

    def on_key_press(self, instance):
        if self.game_over:
            return
        letter = instance.text.upper()
        if self.current_col < self.word_length and self.current_row < self.max_attempts:
            cell_btn = self.cells[self.current_row][self.current_col]
            cell_btn.text = letter
            cell_btn.background_color = (0.15, 0.3, 0.15, 1)  # Koyu yeşil kutu
            cell_btn.color = (1, 1, 1, 1)  # Beyaz harfler
            self.current_col += 1

    def on_backspace(self, instance):
        if self.game_over or self.current_col == 0:
            return
        self.current_col -= 1
        cell_btn = self.cells[self.current_row][self.current_col]
        cell_btn.text = ""
        cell_btn.background_color = (0.15, 0.3, 0.15, 1)
        cell_btn.color = (1, 1, 1, 1)

    def on_enter(self, instance):
        if self.game_over or self.current_col < self.word_length:
            return
        guess = "".join([self.cells[self.current_row][c].text for c in range(self.word_length)]).upper()
        word_dict = {3: self.word_list_3, 4: self.word_list_4, 5: self.word_list_5, 6: self.word_list_6, 7: self.word_list_7}
        valid_words = word_dict.get(self.word_length, self.word_list_5)
        if guess not in valid_words:
            Popup(title="Hata", content=Label(text="Geçersiz kelime!", font_size='22sp'), size_hint=(0.7, 0.3)).open()
            return

        try:
            target_letters = list(self.target)
            guess_letters = list(guess)
            result_colors = ["gray"] * self.word_length

            for i in range(self.word_length):
                if guess_letters[i] == target_letters[i]:
                    result_colors[i] = "green"
                    target_letters[i] = None

            for i in range(self.word_length):
                if result_colors[i] == "gray" and guess_letters[i] in target_letters:
                    result_colors[i] = "yellow"
                    target_letters[target_letters.index(guess_letters[i])] = None

            for i in range(self.word_length):
                cell_btn = self.cells[self.current_row][i]
                letter = guess_letters[i]
                if result_colors[i] == "green":
                    cell_btn.background_color = (0.0, 0.7, 0.0, 1)
                    cell_btn.color = (1, 1, 1, 1)
                elif result_colors[i] == "yellow":
                    cell_btn.background_color = (1.0, 0.84, 0.0, 1)
                    cell_btn.color = (0, 0, 0, 1)
                else:
                    cell_btn.background_color = (0.3, 0.3, 0.3, 1)
                    cell_btn.color = (1, 1, 1, 1)

                key_btn = self.key_buttons.get(letter)
                if key_btn:
                    prev = key_btn.background_color
                    if result_colors[i] == "green":
                        key_btn.background_color = (0.0, 0.7, 0.0, 1)
                        key_btn.color = (1, 1, 1, 1)
                    elif result_colors[i] == "yellow" and prev != [0.0, 0.7, 0.0, 1]:
                        key_btn.background_color = (1.0, 0.84, 0.0, 1)
                        key_btn.color = (0, 0, 0, 1)
                    elif prev not in ([0.0, 0.7, 0.0, 1], [1.0, 0.84, 0.0, 1]):
                        key_btn.background_color = (0.3, 0.3, 0.3, 1)
                        key_btn.color = (1, 1, 1, 1)

            if all(c == "green" for c in result_colors):
                self.show_end_popup(True)
                self.game_over = True
                return
            if self.current_row == self.max_attempts - 1:
                self.show_end_popup(False)
                self.game_over = True
                return

            self.current_row += 1
            self.current_col = 0

        except Exception as e:
            traceback.print_exc()
            Popup(title="Hata (enter)", content=Label(text=str(e), font_size='20sp'), size_hint=(0.8, 0.4)).open()

    def show_end_popup(self, correct: bool):
        msg = f"Tebrikler! '{self.target}' kelimesini buldunuz." if correct else f"Oyunu kaybettiniz! Doğru kelime: '{self.target}'"
        Popup(title="Oyun Bitti", content=Label(text=msg, font_size='24sp'), size_hint=(0.8, 0.4)).open()

    def load_word_lists(self):
        filename = "words_alpha.txt"
        self.word_list_3, self.word_list_4, self.word_list_5, self.word_list_6, self.word_list_7 = [], [], [], [], []
        if os.path.isfile(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        w = line.strip().upper()
                        if w.isalpha():
                            length = len(w)
                            if length == 3:
                                self.word_list_3.append(w)
                            elif length == 4:
                                self.word_list_4.append(w)
                            elif length == 5:
                                self.word_list_5.append(w)
                            elif length == 6:
                                self.word_list_6.append(w)
                            elif length == 7:
                                self.word_list_7.append(w)
            except Exception:
                traceback.print_exc()
        if not self.word_list_3:
            self.word_list_3 = ["CAT", "DOG", "SUN", "MAP"]
        if not self.word_list_4:
            self.word_list_4 = ["TREE", "FISH", "WIND", "MOON"]
        if not self.word_list_5:
            self.word_list_5 = ["APPLE", "BRAIN", "CRANE", "EAGLE", "PLANT"]
        if not self.word_list_6:
            self.word_list_6 = ["MARKET", "GARDEN", "BOTTLE", "WINDOW"]
        if not self.word_list_7:
            self.word_list_7 = ["CAPTURE", "FANTASY", "ORANGEY", "PICTURE"]

if __name__ == "__main__":
    try:
        EverydleApp().run()
    except Exception:
        traceback.print_exc()