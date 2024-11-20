import sqlite3

DB_FILE = "quiz_app.db"

def db_connect():
    return sqlite3.connect(DB_FILE)

# Database Setup
def setup_database():
    with db_connect() as conn:
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                answer TEXT NOT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
            )
        ''')
        conn.commit()

def populate_database():
    with db_connect() as conn:
        cursor = conn.cursor()

        # Seed quizzes
        quizzes = [("Python",), ("DBMS",), ("DSA",)]
        cursor.executemany("INSERT OR IGNORE INTO quizzes (name) VALUES (?)", quizzes)

        # Seed questions
        questions = [
            # Python Quiz
            (1, "Which of the following is a Python keyword?", "for,foreach,loop,repeat", "for"),
            (1, "What is the output of `print(10 // 3)`?", "3,3.3,Error,None", "3"),
            (1, "What does the `len()` function do?", "Returns length,Sorts list,Reverses list,Checks type", "Returns length"),
            (1, "Which library is commonly used for numerical computation in Python?", "numpy,flask,django,pandas", "numpy"),
            (1, "What is the purpose of `if __name__ == '__main__':`?", "Execute code,Import module,Define variable,Start loop", "Execute code"),

            # DBMS Quiz
            (2, "Which of the following is NOT an SQL command?", "UPDATE,SELECT,MODIFY,DELETE", "MODIFY"),
            (2, "What is a foreign key used for?", "Data redundancy,Data security,Establish relationship,Define index", "Establish relationship"),
            (2, "Which normal form removes partial dependency?", "1NF,2NF,3NF,BCNF", "2NF"),
            (2, "Which database model uses tables to represent data?", "Hierarchical,Relational,Object-Oriented,Network", "Relational"),
            (2, "What is the main purpose of indexing?", "Speed up queries,Normalize data,Reduce redundancy,Secure data", "Speed up queries"),

            # DSA Quiz
            (3, "What is the time complexity of linear search?", "O(1),O(n),O(log n),O(n^2)", "O(n)"),
            (3, "Which data structure uses FIFO (First In, First Out)?", "Queue,Stack,Graph,Tree", "Queue"),
            (3, "Which algorithm finds the shortest path in a graph?", "Dijkstra's,Bubble Sort,DFS,Insertion Sort", "Dijkstra's"),
            (3, "What is a binary tree with every level filled called?", "Full tree,Complete tree,AVL tree,BST", "Complete tree"),
            (3, "Which data structure is ideal for implementing recursion?", "Queue,Stack,Array,Linked List", "Stack"),
        ]
        cursor.executemany("INSERT OR IGNORE INTO quiz_questions (quiz_id, question, options, answer) VALUES (?, ?, ?, ?)", questions)
        conn.commit()


# User Management
def register():
    email = input("Enter your email: ").strip().lower()
    password = input("Enter your password: ").strip()

    with db_connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            print("Registration successful!")
        except sqlite3.IntegrityError:
            print("Email already registered!")

def login():
    email = input("Enter your email: ").strip().lower()
    password = input("Enter your password: ").strip()

    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        if user:
            print("Login successful!")
            return user[0]  # Return user ID
        else:
            print("Invalid email or password.")
            return None

# Quiz Management
def quiz_option():
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM quizzes")
        return cursor.fetchall()

def quiz(user_id):
    quizzes = quiz_option()

    print("\nAvailable Quizzes:")
    for idx, (quiz_id, name) in enumerate(quizzes, start=1):
        print(f"{idx}. {name}")

    choice = input("Choose a quiz by number: ").strip()
    try:
        quiz_id = quizzes[int(choice) - 1][0]
    except (IndexError, ValueError):
        print("Invalid choice.")
        return

    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT question, options, answer FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
        questions = cursor.fetchall()

        if not questions:
            print("No questions available for this quiz.")
            return

        score = 0
        for question, options, answer in questions:
            print(f"\n{question}")
            options = options.split(",")  # Assuming options stored as "A,B,C,D"
            for idx, opt in enumerate(options, start=1):
                print(f"{idx}. {opt}")

            user_answer = input("Your answer: ").strip()
            try:
                if options[int(user_answer) - 1] == answer:
                    score += 1
            except (IndexError, ValueError):
                print("Invalid answer.")
        print(f"\nYou scored {score}/{len(questions)}!")
        cursor.execute("INSERT INTO user_scores (user_id, quiz_id, score) VALUES (?, ?, ?)", (user_id, quiz_id, score))
        conn.commit()

# Show Results
def show_results(user_id):
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT quizzes.name, user_scores.score 
            FROM user_scores 
            JOIN quizzes ON user_scores.quiz_id = quizzes.id 
            WHERE user_scores.user_id = ?
        """, (user_id,))
        results = cursor.fetchall()

    if results:
        print("\nYour Quiz Results:")
        for quiz_name, score in results:
            print(f"Quiz: {quiz_name}, Score: {score}")
    else:
        print("No quiz attempts found.")

# Main Menu
def main():
    current_user_id = None

    # Setup and populate database
    setup_database()
    populate_database()

    while True:
        print("\n1. Register\n2. Login\n3. Take Quiz\n4. Show Results\n5. Exit")
        choice = input("Select an option: ").strip()

        if choice == '1':
            register()
        elif choice == '2':
            current_user_id = login()
        elif choice == '3':
            if current_user_id:
                quiz(current_user_id)
            else:
                print("Please log in first!")
        elif choice == '4':
            if current_user_id:
                show_results(current_user_id)
            else:
                print("Please log in first!")
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
