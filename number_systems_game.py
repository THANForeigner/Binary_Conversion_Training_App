import flet as ft
import random
import math
from game_logic import (
    generate_conversion_question,
    generate_power_of_two_question,
    generate_IEEE_question,
    BITS,
)

def main(page: ft.Page):
    page.title = "Number Systems Quiz"
    page.theme_mode = "dark"
    page.bgcolor = ft.Colors.BLACK
    page.window_width = 900
    page.window_height = 650
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    score = 0
    quiz_data = {}
    state = "menu"

    # --- UI ELEMENTS ---
    title_text = ft.Text("Number Systems Trainer", size=50, color="amber500", weight="bold")
    subtitle = ft.Text("Test your knowledge of binary, powers of two, and IEEE 754!", size=20, color="white70")
    score_text = ft.Text("Score: 0", size=24, color="green400")
    question_text = ft.Text("", size=26, color="white", text_align="center", weight="bold")
    feedback_text = ft.Text("", size=22, color="red500", text_align="center", weight="bold")

    # Input field — used for all question types
    input_field = ft.TextField(
        value="",
        width=500,
        height=55,
        text_align="center",
        bgcolor="bluegrey900",
        color="white",
        border_radius=8,
        hint_text="Enter your answer...",
        border_color="blue400",
    )

    # --- Buttons ---
    submit_button = ft.ElevatedButton("Submit", bgcolor="blue500", color="white", width=160, height=50)
    next_button = ft.ElevatedButton("Next Question", bgcolor="amber500", color="white", width=160, height=50, visible=False)
    giveup_button = ft.ElevatedButton("Give Up", bgcolor="red600", color="white", width=160, height=50, visible=False)
    menu_button = ft.ElevatedButton("Main Menu", bgcolor="grey700", color="white", width=160, height=45)

    # --- Menu View ---
    menu_view = ft.Column(
        [
            title_text,
            subtitle,
            ft.Divider(height=40, color="transparent"),
            ft.ElevatedButton("1. Power of Two Quiz", width=350, height=60,
                              on_click=lambda _: set_state("power"), bgcolor="blue500", color="white"),
            ft.ElevatedButton("2. Binary Conversion Quiz", width=350, height=60,
                              on_click=lambda _: set_state("binary"), bgcolor="blue500", color="white"),
            ft.ElevatedButton("3. IEEE 754 Float Quiz", width=350, height=60,
                              on_click=lambda _: set_state("ieee"), bgcolor="blue500", color="white"),
            ft.Text(f"Using {BITS}-bit representation.", size=16, color="white30"),
        ],
        alignment="center",
        horizontal_alignment="center",
        expand=True,
    )

    # --- Quiz View ---
    quiz_view = ft.Column(
        [
            ft.Row([score_text], alignment="end", width=600),
            ft.Text("Quiz Mode", size=36, color="white", weight="bold"),
            ft.Divider(height=30, color="transparent"),
            question_text,
            ft.Divider(height=10, color="transparent"),
            input_field,
            ft.Divider(height=10, color="transparent"),
            ft.Row([submit_button, next_button, giveup_button],
                   alignment="center", spacing=20),
            ft.Divider(height=10, color="transparent"),
            feedback_text,
            ft.Container(expand=True),
            menu_button,
        ],
        alignment="start",
        horizontal_alignment="center",
        expand=True,
        visible=False,
    )

    layout = ft.Stack([menu_view, quiz_view], expand=True)
    page.add(layout)

    # --- Core Functions ---
    def set_state(new_state):
        nonlocal state, score
        state = new_state
        score = 0
        score_text.value = f"Score: {score}"

        if new_state == "menu":
            menu_view.visible = True
            quiz_view.visible = False
        else:
            menu_view.visible = False
            quiz_view.visible = True
            start_new_question()
        page.update()

    def start_new_question():
        nonlocal quiz_data
        feedback_text.value = ""
        feedback_text.color = "red500"
        input_field.value = ""
        submit_button.visible = True
        next_button.visible = False
        giveup_button.visible = False

        if state == "power":
            q, ans = generate_power_of_two_question()
            quiz_data = {"question": q, "correct_ans": ans, "type": "int"}
            input_field.hint_text = "Enter a whole number..."
        elif state == "binary":
            q, ans, bits = generate_conversion_question()
            quiz_data = {"question": q, "correct_ans": ans, "type": "binary"}
            input_field.hint_text = f"Enter a {bits}-bit binary string..."
        elif state == "ieee":
            q, ans = generate_IEEE_question()
            quiz_data = {"question": q, "correct_ans": ans, "type": "ieee"}
            input_field.hint_text = "Enter 32-bit IEEE binary (auto-spaced every 4 bits)..."

        question_text.value = quiz_data.get("question", "")
        page.update()

    # --- Auto-space after every 4 bits ---
    def auto_space(e: ft.ControlEvent):
        raw = e.control.value.replace(" ", "")
        spaced = " ".join([raw[i:i+4] for i in range(0, len(raw), 4)])
        if e.control.value != spaced:
            e.control.value = spaced
            page.update()

    input_field.on_change = auto_space

    # --- Validation ---
    def process_submission(e):
        nonlocal score
        user_input = input_field.value.strip().replace(" ", "")
        if not user_input:
            feedback_text.value = "Please enter an answer!"
            page.update()
            return

        ans = quiz_data.get("correct_ans", "")
        qtype = quiz_data.get("type", "")
        correct = False

        if qtype == "int":
            try:
                if str(int(user_input)) == str(ans):
                    correct = True
                else:
                    feedback_text.value = "Wrong answer."
                    giveup_button.visible = True
            except ValueError:
                feedback_text.value = "Invalid number input."

        elif qtype == "binary":
            if len(user_input) != BITS:
                feedback_text.value = f"Must be exactly {BITS} bits."
            elif all(c in "01" for c in user_input):
                if user_input == ans:
                    correct = True
                else:
                    feedback_text.value = "Incorrect binary!"
                    giveup_button.visible = True
            else:
                feedback_text.value = "Use only 0 and 1."

        elif qtype == "ieee":
            if len(user_input) != 32:
                feedback_text.value = "IEEE 754 float must be 32 bits."
            elif all(c in "01" for c in user_input):
                if user_input == ans:
                    correct = True
                else:
                    feedback_text.value = "Incorrect IEEE value!"
                    giveup_button.visible = True
            else:
                feedback_text.value = "Use only 0 and 1."

        if correct:
            feedback_text.value = "Correct! 🎉"
            feedback_text.color = "green400"
            score += 1
            score_text.value = f"Score: {score}"
            submit_button.visible = False
            next_button.visible = True
            giveup_button.visible = False
        else:
            submit_button.visible = True
            next_button.visible = False

        page.update()

    def give_up(e):
        ans = quiz_data.get("correct_ans", "")
        if quiz_data.get("type") == "ieee":
            formatted = f"{ans[0]} | {ans[1:9]} | {ans[9:]}"
            feedback_text.value = f"The correct IEEE answer:\n{formatted}"
        else:
            feedback_text.value = f"The correct answer is:\n{ans}"
        feedback_text.color = "amber400"
        submit_button.visible = False
        next_button.visible = True
        giveup_button.visible = False
        page.update()

    # --- Bindings ---
    submit_button.on_click = process_submission
    next_button.on_click = lambda e: start_new_question()
    giveup_button.on_click = give_up
    menu_button.on_click = lambda e: set_state("menu")

    set_state("menu")

if __name__ == "__main__":
    ft.app(target=main)
