from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session 
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="cset155",
        database= "rj_bank"
    )