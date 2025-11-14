#!/usr/bin/env python3
import argparse
import sqlite3
import sys
from pathlib import Path

DB_FILE = Path.home() / '.task_cli.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_task(description):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (description) VALUES (?)', (description,))
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    print(f'Task added with id {task_id}')

def list_tasks():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id, description, done FROM tasks ORDER BY id')
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print('No tasks found.')
        return
    for task_id, desc, done in rows:
        status = '✓' if done else '○'
        print(f'{task_id:>3} {status} {desc}')

def delete_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    if deleted:
        print(f'Task {task_id} deleted.')
    else:
        print(f'Task {task_id} not found.')

def main():
    parser = argparse.ArgumentParser(
        prog='task-cli',
        description='Simple CLI task manager with SQLite storage'
    )
    sub = parser.add_subparsers(dest='command', required=True)

    p_add = sub.add_parser('add', help='Add a new task')
    p_add.add_argument('description', help='Task description')

    p_list = sub.add_parser('list', help='List all tasks')

    p_del = sub.add_parser('delete', help='Delete a task')
    p_del.add_argument('id', type=int, help='Task id to delete')

    args = parser.parse_args()
    init_db()

    if args.command == 'add':
        add_task(args.description)
    elif args.command == 'list':
        list_tasks()
    elif args.command == 'delete':
        delete_task(args.id)

if __name__ == '__main__':
    main()