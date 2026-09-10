CREATE TABLE habits (
    habit_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    content TEXT NOT NULL,
    date_created DATE DEFAULT CURRENT_DATE,
    user_id INT NOT NULL REFERENCES users(user_id)
);