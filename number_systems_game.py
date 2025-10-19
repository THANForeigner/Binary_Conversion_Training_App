import flet as ft
import random

BITS = 16
SIGNED_MAX = 2 ** (BITS - 1) - 1
SIGNED_MIN = -(2 ** (BITS - 1))


def to_binary(n, bits=BITS):
    if n < 0:
        return "ERROR_NEG"
    return bin(n)[2:].zfill(bits)


def to_one_complement(n, bits=BITS):
    if n >= 0:
        if n > 2 ** (bits - 1) - 1:
            return "OVERFLOW_POS"
        return "0" + to_binary(n, bits=bits - 1)
    else:
        magnitude = abs(n)
        if magnitude > 2 ** (bits - 1) - 1:
            return "OVERFLOW_NEG"
        standard_bin = to_binary(magnitude, bits=bits - 1)
        inverted = ''.join('1' if b == '0' else '0' for b in standard_bin)
        return "1" + inverted


def to_two_complement(n, bits=BITS):
    if n > 2 ** (bits - 1) - 1:
        return "OVERFLOW_POS"
    if n < -(2 ** (bits - 1)):
        return "OVERFLOW_NEG"
    return bin(n & (2 ** bits - 1))[2:].zfill(bits)


def bias_binary_conversion(n, bits=BITS):
    K = (2 ** (bits - 1)) - 1
    biased = n + K
    if biased < 0 or biased > (2 ** bits - 1):
        return "BIAS_RANGE_ERROR"
    return to_binary(biased, bits)


def generate_power_of_two_question():
    k = random.randint(3, 10)
    return f"What is the value of 2^{k}?", str(2 ** k)


def generate_conversion_question():
    n = random.randint(SIGNED_MIN // 8, SIGNED_MAX // 8)
    sit = random.randint(1, 3)
    bits = BITS

    if sit == 1:
        q = f"Show the 1's Complement of {n} with {bits} bits:"
        ans = to_one_complement(n, bits)
    elif sit == 2:
        q = f"Show the 2's Complement of {n} with {bits} bits:"
        ans = to_two_complement(n, bits)
    else:
        K = (2 ** (bits - 1)) - 1
        max_n = (2 ** bits - 1) - K
        min_n = 0 - K
        n = random.randint(min_n, max_n)
        q = f"Show the Bias ({K}) Binary Conversion of {n} with {bits} bits:"
        ans = bias_binary_conversion(n, bits)
    return q, ans, bits


def main(page: ft.Page):
    # Basic setup
    page.title = "Number Systems Quiz"
    page.theme_mode = "dark"
    page.bgcolor = "black"
    page.window_width = 800
    page.window_height = 600
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # Game state
    score = 0
    quiz_data = {}
    state = "menu"  # or "power", "binary"

    # UI elements
    title_text = ft.Text("Number Systems Trainer", size=48, color="amber500", weight="bold")
    score_text = ft.Text("Score: 0", size=24, color="green400")
    question_text = ft.Text("", size=24, color="white", text_align="center")

    input_field = ft.TextField(
        value="", width=400, height=50, text_align="center",
        bgcolor="bluegrey800", color="white", border_radius=5,
        hint_text="Enter your answer...", border_color="blue400"
    )

    feedback_text = ft.Text("", size=24, color="red500", text_align="center")

    submit_button = ft.ElevatedButton("Submit", bgcolor="blue500", color="white")
    next_button = ft.ElevatedButton("Next Question", bgcolor="amber500", color="white", visible=False)
    menu_button = ft.ElevatedButton("Main Menu", bgcolor="grey700", color="white")

    # --- Page containers ---
    menu_view = ft.Column(
        [
            title_text,
            ft.Text("Select a Quiz Mode to begin training.", size=20, color="white70"),
            ft.Divider(height=50, color="transparent"),
            ft.ElevatedButton(
                "1. Power of Two Quiz", width=300, height=60,
                on_click=lambda _: set_state("power"), bgcolor="blue500", color="white"
            ),
            ft.ElevatedButton(
                "2. Binary Conversion Quiz", width=300, height=60,
                on_click=lambda _: set_state("binary"), bgcolor="blue500", color="white"
            ),
            ft.Text(f"Using {BITS}-bit representation.", size=16, color="white30"),
        ],
        alignment="center",
        horizontal_alignment="center",
        expand=True
    )

    quiz_view = ft.Column(
        [
            ft.Row([score_text], alignment="end", width=400),
            ft.Text("Quiz", size=36, color="white", weight="bold"),
            ft.Divider(height=40, color="transparent"),
            question_text,
            ft.Divider(height=10, color="transparent"),
            input_field,
            ft.Row([submit_button, next_button], alignment="center"),
            ft.Divider(height=10, color="transparent"),
            feedback_text,
            ft.Container(expand=True),
            menu_button,
        ],
        alignment="start",
        horizontal_alignment="center",
        expand=True,
        visible=False
    )

    layout = ft.Stack([menu_view, quiz_view], expand=True)
    page.add(layout)

    # --- State management functions ---
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

        if state == "power":
            q, ans = generate_power_of_two_question()
            input_field.max_length = 10
            input_field.hint_text = "Enter a whole number..."
            quiz_data = {"question": q, "correct_ans": ans, "type": "int"}
        elif state == "binary":
            q, ans, bits = generate_conversion_question()
            input_field.max_length = bits
            input_field.hint_text = f"Enter a {bits}-bit binary string..."
            quiz_data = {"question": q, "correct_ans": ans, "type": "binary"}

        question_text.value = quiz_data["question"]
        page.update()

    def process_submission(e):
        nonlocal score
        user_input = input_field.value.strip()
        if not user_input:
            feedback_text.value = "Please enter an answer!"
            page.update()
            return

        ans = quiz_data.get("correct_ans", "")
        qtype = quiz_data.get("type", "")
        correct = False

        if qtype == "int":
            try:
                if str(int(user_input)) == ans:
                    correct = True
                else:
                    feedback_text.value = f"Wrong answer. Correct: {ans}"
            except ValueError:
                feedback_text.value = "Invalid input. Enter a number."
        elif qtype == "binary":
            cleaned = user_input.replace(" ", "")
            if len(cleaned) != BITS:
                feedback_text.value = f"Must be exactly {BITS} bits."
            elif all(c in "01" for c in cleaned):
                if cleaned == ans:
                    correct = True
                else:
                    feedback_text.value = f"Wrong! Correct: {ans}"
            else:
                feedback_text.value = "Use only 0 and 1."

        if correct:
            feedback_text.value = "Correct! 🎉"
            feedback_text.color = "green400"
            score += 1
            score_text.value = f"Score: {score}"
            submit_button.visible = False
            next_button.visible = True
        else:
            submit_button.visible = True
            next_button.visible = False

        page.update()

    submit_button.on_click = process_submission
    next_button.on_click = lambda e: start_new_question()
    menu_button.on_click = lambda e: set_state("menu")

    # Start at menu
    set_state("menu")


if __name__ == "__main__":
    ft.app(target=main)
